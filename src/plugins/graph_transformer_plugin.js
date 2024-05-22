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
                // ...["", "In", "Out", "Inbound", "Outbound", "Directed", "Undirected"].flatMap(variant => [
                //     `forEach${variant}Edge`, `map${variant}Edges`, `filter${variant}Edges`, `reduce${variant}Edges`, `find${variant}Edge`, `some${variant}Edge`, `every${variant}Edge`
                // ]), // TODO: add edges support
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
                    const action = commandNamePrefix === 'reduce' ?
                        new Function(accumulator, as, `return ${baseAction}`) :
                        new Function(as, `return ${baseAction}`)
                    let callback = () => {}
                    if (commandName.includes('Edge')) {
                        throw new Error("Edges not supported yet") // TODO
                    } else {
                        const createNodeProxy = (key, attrs) => {
                            return new Proxy(attrs, {
                                get: function(attrs, prop) {
                                    if (prop === 'key' || prop === 'id') return key
                                    if (prop === 'attributes' || prop === 'attrs') return attrs
                                    return attrs[prop]
                                }
                            })
                        }
                        if (commandNamePrefix === 'reduce') {
                            const initialValue = resolveValue(command[commandName].initialValue || command[commandName].initial, context, {})
                            callback = (acc, key, attrs) => action(acc, createNodeProxy(key, attrs))
                            result = graph[commandName](callback, initialValue)
                        } else {
                            callback = (key, attrs) => action(createNodeProxy(key, attrs))
                            result = graph[commandName](callback)
                        }
                    }
                } else {
                    const action = new Function("return " + (command[commandName].action || command[commandName].function))()
                    result = graph[commandName](action)
                }

                if (commandName.includes('Node') && command[commandName].resolve_nodes) {
                    result = result.map(key => ({
                        key,
                        ...graph.getNodeAttributes(key),
                    }))
                } else if (commandName.includes('Edge') && command[commandName].resolve_edges) {
                    result = result.map(key => ({
                        key,
                        ...graph.getEdgeAttributes(key),
                    }))
                    //TODO: add source and target?
                }

                if (!_.isUndefined(result)) _.set(context, command[commandName].into, result)

                return context
            }
        },
    ]
}
