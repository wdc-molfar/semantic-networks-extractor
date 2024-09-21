import _ from 'lodash';
import { resolveValue, resolveContextVariables } from '../utils';
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
            name: ['forEach', 'iterate'],
            _execute: async (command, context) => {
                command.forEach = command.forEach || command.iterate;
                command.forEach.do =
                    command.forEach.do || command.forEach.execute;
                const collection = resolveValue(
                    command.forEach.collection ||
                        command.forEach.of ||
                        command.forEach.from,
                    context,
                    []
                );
                const as =
                    command.forEach.as ||
                    command.forEach.item ||
                    command.forEach.element ||
                    '$item';
                for (const element of collection) {
                    context[as] = element;
                    for (const subCommand of command.forEach.do) {
                        context = await extractorInstance.executeOnce(
                            subCommand,
                            context
                        );
                    }
                }
                return context;
            },
        },
        {
            name: ['while'],
            _execute: async (command, context) => {
                command.while.condition =
                    command.while.condition || command.while.check;
                command.while.do = command.while.do || command.while.execute;
                const conditionCheckFunc = new Function(
                    'context',
                    `return ${resolveContextVariables(command.while.condition.toString())}`
                );
                while (conditionCheckFunc(context)) {
                    for (const subCommand of command.while.do) {
                        context = await extractorInstance.executeOnce(
                            subCommand,
                            context
                        );
                    }
                }
                return context;
            },
        },
        {
            name: ['if'],
            _execute: async (command, context) => {
                command.if.condition = command.if.condition || command.if.check;

                const conditionCheckFunc = new Function(
                    'context',
                    `return ${resolveContextVariables(command.if.condition.toString())}`
                );

                if (conditionCheckFunc(context)) {
                    for (const subCommand of command.if.then ?? []) {
                        context = await extractorInstance.executeOnce(
                            subCommand,
                            context
                        );
                    }
                } else {
                    for (const subCommand of command.if.else ?? []) {
                        context = await extractorInstance.executeOnce(
                            subCommand,
                            context
                        );
                    }
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
                    context,
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
