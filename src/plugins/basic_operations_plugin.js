const _ = require("lodash")
const { resolveValue } = require("../utils/values")


let extractorInstance = {}

const transform = async (script, value, context) => {
    try {
        script = script || "value => value"
        return (await eval(script)(value, context))
    } catch(e) {
        throw new Error(`Cannot execute transform:\n${script}\n${e.toString()}`)
    }
}

module.exports = {
    register: extractor => {
        extractorInstance = extractor
    },
    commands: [
        {
            name: ["aggregate", "context"],
            _execute: async (command, context) => {
                command.aggregate = command.aggregate || command.context
                for (let i = 0; i < command.aggregate.length; i++) {
                    context = await extractorInstance.executeOnce(command.aggregate[i], context)
                }
                return context
            }
        },
        {
            name: ["transform"],
            _execute: async (command, context) => {
                const inputValue = resolveValue(command.transform.from || command.transform.variable, context, undefined)
                const value = await transform(command.transform.action || command.transform.function, inputValue, context)
                _.set(context, command.transform.to || command.transform.into, value)
                return context
            }
        },
        {
            name: ["value", "const"],
            _execute: async (command, context) => {
                const value = await transform( command.value.transform || command.value.set, undefined, context)
                _.set(context, command.value.into, value)
                return context
            }
        },
    ]
}
