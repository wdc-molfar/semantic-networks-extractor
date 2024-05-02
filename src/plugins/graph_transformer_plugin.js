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
    ]
}
