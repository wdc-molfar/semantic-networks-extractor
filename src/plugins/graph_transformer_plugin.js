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
                graph.import(inputValue)
                _.set(context, command.import_graph.into, graph)
                return context
            }
        },
        {
            name: ["export_graph"],
            _execute: async (command, context) => {
                const graph = resolveValue(command.export_graph.from || command.export_graph.graph, context, {})
                const exportedGraph = graph.export()
                _.set(context, command.export_graph.into || command.export_graph.to, exportedGraph)
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
