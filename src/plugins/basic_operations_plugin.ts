import _ from 'lodash';
import { resolveValue } from '../utils/values';
import { Context, Executor, Plugin } from '../types';

let extractorInstance: Executor;

const transform = async (script: string, value: any, context: Context) => {
    try {
        script = script || 'value => value';
        return await eval(script)(value, context);
    } catch (e: any) {
        throw new Error(
            `Cannot execute transform:\n${script}\n${e.toString()}`
        );
    }
};

const plugin: Plugin = {
    register: (extractor) => {
        extractorInstance = extractor;
    },
    commands: [
        {
            name: ['aggregate'],
            _execute: async (command, context) => {
                for (let i = 0; i < command.aggregate.length; i++) {
                    context = await extractorInstance.executeOnce(
                        command.aggregate[i],
                        context
                    );
                }
                return context;
            },
        },
        {
            name: ['transform', 'context'],
            _execute: async (command, context) => {
                command.transform = command.transform || command.context;
                const inputValue = resolveValue(
                    command.transform.from || command.transform.variable,
                    context,
                    undefined
                );
                const value = await transform(
                    command.transform.action || command.transform.function,
                    inputValue,
                    context
                );
                _.set(
                    context,
                    command.transform.to || command.transform.into,
                    value
                );
                return context;
            },
        },
        {
            name: ['value', 'const'],
            _execute: async (command, context) => {
                command.value = command.value || command.const;
                const value = await transform(
                    command.value.transform || command.value.set,
                    undefined,
                    context
                );
                _.set(context, command.value.into, value);
                return context;
            },
        },
        {
            name: ['delete', 'remove'],
            _execute: async (command, context) => {
                _.unset(context, command.delete || command.remove);
                return context;
            },
        },
    ],
};

export default plugin;
