const _ = require("lodash")
const Graph = require("graphology")
const { resolveValue } = require("../utils/values")

module.exports = {
    commands: [
        {
            name: ["import_graph"],
            _execute: async (command, context) => {
                const inputValue = resolveValue(command.import_graph.from, context, {})
                const graph = new Graph({
                    allowSelfLoops: !!command.import_graph.allowSelfLoops || true,
                    multi: !!command.import_graph.multi || false,
                    type: command.import_graph.type || "mixed"
                })

                let formatter
                switch (command.import_graph.format?.toLowerCase()) {
                    case "echarts":
                        formatter = ({ dependencies: { data, nodes, links, edges, categories, ...deps_info }, ...data_info }) => ({
                            nodes: (data ?? nodes).map(({ id, ...attributes }) => ({ key: id, attributes: { ...attributes, category: categories[attributes.category].name } })),
                            edges: (links ?? edges).map(({ source, target, ...attributes }) => ({ key: `(${source})->(${target})`, source, target, attributes })),
                            attributes: { ...data_info, ...deps_info },
                        })
                        break
                    case "graphology":
                    case null:
                    case undefined:
                        formatter = (value) => value
                        break
                    default:
                        formatter = new Function("return " + command.import_graph.format)()
                        break
                }

                graph.import(formatter(inputValue))

                if (command.import_graph.resolve_coreferences) {
                    const coref_nodes = graph.filterNodes(
                        (id, { coreference }) => coreference.length > 0
                    ).map(key => ({
                        key,
                        ...graph.getNodeAttributes(key),
                    }))

                    _.values(_.groupBy(coref_nodes.flatMap(node => node.coreference.map(coref => ({
                        key: node.key,
                        is_representative: coref.is_representative,
                        coref_id: coref.coref_id,
                    }))), 'coref_id')).forEach(coref_group => {
                        const representatives = coref_group.filter(node => node.is_representative)
                        const pronouns = coref_group.filter(node => !node.is_representative)
                        pronouns.forEach(pronoun => {
                            representatives.forEach(representative => {
                                graph.addEdgeWithKey(`(${pronoun.key})->(${representative.key})`, pronoun.key, representative.key, {
                                    value: 'coref',
                                    coref_id: pronoun.coref_id,
                                })
                            })
                        })
                    })

                    graph.forEachNode((key) => {
                        graph.removeNodeAttribute(key, 'coreference')
                    })
                }

                _.set(context, command.import_graph.into, graph)
                return context
            }
        },
        {
            name: ["export_graph"],
            _execute: async (command, context) => {
                const graph = resolveValue(command.export_graph.from || command.export_graph.graph, context, {})
                const exportedGraph = graph.export()
                let formatter
                switch (command.export_graph.format?.toLowerCase()) {
                    case "echarts":
                        formatter = ({ nodes, edges, attributes }) => {
                            const categories = _.uniq(nodes.map(({ attributes }) => attributes.category))
                            return ({
                                ...attributes,
                                dependencies: {
                                    nodes: nodes.map(({ key, attributes }) => ({ id: key, ...attributes, category: categories.indexOf(attributes.category) })),
                                    links: edges.map(({ source, target, attributes: { value, ...other } }) => ({ ...other, source, value, target })),
                                    categories: categories.map(name => ({ name })),
                                },
                            })
                        }
                        break
                    case "graphology":
                    case null:
                    case undefined:
                        formatter = (value) => value
                        break
                    default:
                        formatter = new Function("return " + command.export_graph.format)()
                        break
                }
                _.set(context, command.export_graph.into || command.export_graph.to, formatter(exportedGraph))
                return context
            }
        },
        {
            name: [
                "forEachNode", "mapNodes", "filterNodes", "reduceNodes", "findNode", "someNode", "everyNode",
                ...["Edge", "Neighbor"].flatMap(iteratee => ["", "In", "Out", "Inbound", "Outbound", "Directed", "Undirected"].flatMap(variant => [
                    `forEach${variant}${iteratee}`, `map${variant}${iteratee}s`, `filter${variant}${iteratee}s`, `reduce${variant}${iteratee}s`, `find${variant}${iteratee}`, `some${variant}${iteratee}`, `every${variant}${iteratee}`
                ])),
            ],
            _execute: async (command, context) => {
                const commandName = _.keys(command)[0]
                const graph = resolveValue(command[commandName].from || command[commandName].graph, context, {})
                command[commandName].into = command[commandName].into || command[commandName].to

                let result = undefined
                const as = command[commandName].as
                const accumulator = command[commandName].accumulator || command[commandName].into?.replaceAll('.', '_')
                if (as) {
                    const [commandNamePrefix] = commandName.split(/[A-Z]/, 1)

                    const baseAction = (["filter", "find", "some", "every"].some(prefix => commandNamePrefix === prefix) ?
                        command[commandName].where :
                        (["for", "map"].some(prefix => commandNamePrefix === prefix) ?
                            (command[commandName].each || command[commandName].do) :
                            undefined)) || command[commandName][commandNamePrefix]

                    const createItemProxy = (key, attrs) => {
                        return new Proxy(attrs, {
                            get: function(attrs, prop) {
                                if (prop === 'key' || prop === 'id') return key
                                if (prop === 'attributes' || prop === 'attrs') return attrs
                                return attrs[prop]
                            }
                        })
                    }
                    let callback = () => {}
                    if (commandName.includes('Edge')) {
                        const source = resolveValue(command[commandName].source || command[commandName].from_node, context, undefined)
                        const target = resolveValue(command[commandName].target || command[commandName].to_node, context, undefined)
                        const node = resolveValue(command[commandName].node || command[commandName].of, context, undefined)

                        const nodesParametrization = ((!!source && !!target) ? [source, target] : !!node ? [node] : []).map(node => _.isString(node) ? node : node.key)

                        const defaultFunctionArgs = [as.edge ?? as, as.source ?? '$source', as.target ?? '$target', as.undirected ?? '$undirected']

                        if (commandNamePrefix === 'reduce') {
                            const action = new Function(accumulator, ...defaultFunctionArgs, `return ${baseAction}`)
                            const initialValue = resolveValue(command[commandName].initialValue || command[commandName].initial, context, {})
                            callback = (acc, edgeKey, edgeAttrs, sourceKey, targetKey, sourceAttrs, targetAttrs, undirected) =>
                                action(acc, createItemProxy(edgeKey, edgeAttrs), createItemProxy(sourceKey, sourceAttrs), createItemProxy(targetKey, targetAttrs), undirected)
                            result = graph[commandName](...nodesParametrization, callback, initialValue)
                        } else {
                            const action = new Function(...defaultFunctionArgs, `return ${baseAction}`)
                            callback = (edgeKey, edgeAttrs, sourceKey, targetKey, sourceAttrs, targetAttrs, undirected) =>
                                action(createItemProxy(edgeKey, edgeAttrs), createItemProxy(sourceKey, sourceAttrs), createItemProxy(targetKey, targetAttrs), undirected)
                            result = graph[commandName](...nodesParametrization, callback)
                        }
                    } else {
                        const node = resolveValue(command[commandName].node || command[commandName].of, context, undefined)
                        const nodesParametrization = (commandName.includes('Neighbor') ? [node] : []).map(node => _.isString(node) ? node : node.key)

                        if (commandNamePrefix === 'reduce') {
                            const action = new Function(accumulator, as, `return ${baseAction}`)
                            const initialValue = resolveValue(command[commandName].initialValue || command[commandName].initial, context, {})
                            callback = (acc, key, attrs) => action(acc, createItemProxy(key, attrs))
                            result = graph[commandName](...nodesParametrization, callback, initialValue)
                        } else {
                            const action = new Function(as, `return ${baseAction}`)
                            callback = (key, attrs) => action(createItemProxy(key, attrs))
                            result = graph[commandName](...nodesParametrization, callback)
                        }
                    }
                } else {
                    const action = new Function("return " + (command[commandName].action || command[commandName].function))()
                    result = graph[commandName](action)
                }

                if (commandName.startsWith('find')) result = [result]

                const nodeResolver = (key) => ({ key, ...graph.getNodeAttributes(key) })
                if (commandName.includes('Node') && command[commandName].resolve_nodes) {
                    result = result.map(nodeResolver)
                } else if (commandName.includes('Edge') && command[commandName].resolve_edges) {
                    const resolveSources = command[commandName].resolve_sources || command[commandName].resolve_nodes
                    const resolveTargets = command[commandName].resolve_targets || command[commandName].resolve_nodes
                    result = result.map(key => ({
                        key,
                        source: resolveSources ? nodeResolver(graph.source(key)) : graph.source(key),
                        target: resolveTargets ? nodeResolver(graph.target(key)) : graph.target(key),
                        ...graph.getEdgeAttributes(key),
                    }))
                }

                if (commandName.startsWith('find')) [result] = result

                if (!_.isUndefined(result)) _.set(context, command[commandName].into, result)

                return context
            }
        },
    ]
}
