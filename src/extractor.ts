import {
    isArray,
    keys,
    isString,
    isFunction,
    flatten,
    isObject,
    first,
} from 'lodash';
import YAML from 'js-yaml';
import moment from 'moment';
import { resolveCommand, VariableNameType } from './utils/values';

import plugins from './plugins';
import { Executor, Plugin, Command, Context } from './types';

export default class SemNetExtractor implements Executor {
    #plugins: Plugin[];
    #commandImplementations: Command[];

    constructor() {
        this.#plugins = [];
        this.#commandImplementations = [];
        this.use(plugins);
    }

    use(plugins: Plugin | Plugin[]) {
        plugins = isArray(plugins) ? plugins : [plugins];
        (plugins as Plugin[]).forEach((plugin) => {
            this.#plugins.push(plugin);
            this.register(plugin);
        });
    }

    register(plugins: Plugin | Plugin[]) {
        plugins = isArray(plugins) ? plugins : [plugins];
        (plugins as Plugin[]).forEach((plugin) => {
            if (plugin.register) plugin.register(this);
            this.#commandImplementations = this.#commandImplementations.concat(
                plugin.commands || []
            );
        });
    }

    async executeOnce(
        command: Record<string, any>,
        context: Context,
        sender?: any
    ) {
        // context.$log = context.$log || []
        //       context.$log += `\n[ ${moment(new Date()).format("YYYY.MM.DD HH:mm:ss")} ]:\n${YAML.dump(command)}`

        const commandName = first(keys(command));
        if (!commandName) throw new Error('Empty command name');
        console.log(commandName);
        const executors = this.#commandImplementations.filter((rule) =>
            rule.name.includes(commandName)
        );
        if (executors.length >= 2) {
            throw new Error(
                `Multiple determination of "${commandName}". Command aliases (${flatten(executors.map((e) => e.name)).join(', ')}) required.`
            );
        }
        let executor = executors[0];

        if (executor) {
            if (!isFunction(executor)) {
                if (executor._execute) {
                    executor = executor._execute;
                } else {
                    throw new Error(
                        `"${isArray(executor.name) ? executor.name[0] : executor.name}: _execute" command not implemented`
                    );
                }
            }

            try {
                command = resolveCommand(command as VariableNameType, context);
                const ctx = await executor(command, context, sender);
                context = isObject(ctx)
                    ? !isArray
                        ? Object.assign({}, context, ctx)
                        : ctx
                    : ctx;
                return context;
            } catch (e) {
                throw e;
            }
        } else {
            throw new Error(`"${commandName}" command not implemented`);
        }
    }

    async execute(script: string | Record<string, any>[], context: Context) {
        let i = 0;

        try {
            if (!script) return context;

            if (isString(script)) {
                script = YAML.load(script.replace(/\t/gm, ' ')) as Record<
                    string,
                    any
                >[];
            }

            script = isArray(script) ? script : [script];
            context = context || {};

            context._log = '';

            for (i = 0; i < script.length; i++) {
                let ctx = await this.executeOnce(script[i], context);
                context = ctx ? ctx : context;
            }
        } catch (e: any) {
            console.error(e);
            context._error = ` Error at script position ${i}.\n${YAML.dump(script[i])}\n${e?.toString()}`;
        } finally {
            for (let i = 0; i < this.#plugins.length; i++) {
                await this.#plugins[i].close?.();
            }

            if (context._error) {
                context._log += `\n[ ${moment(new Date()).format('YYYY.MM.DD HH:mm:ss')} ]: Semantic network corrupted due to errors`;
                context._log += `\n${context._error}`;
            } else {
                context._log += `\n[ ${moment(new Date()).format('YYYY.MM.DD HH:mm:ss')} ]: Semantic network built successfully`;
            }
            // context.$log += `\n[ ${moment(new Date()).format("YYYY.MM.DD HH:mm:ss")} ]: Semantic network context`

            // let loggedContextFields = keys(context).filter( key => !key.startsWith("$"))

            // context.$log +=`{\n`

            // loggedContextFields.forEach( key => {
            // 	context.$log +=`${key}: `
            // 	let data = context[key]
            // 	let res
            // 	if(isArray(data) && data.length > 5 ){
            // 		res = data.map(d => JSON.stringify(d, null," ")).slice(0,6)
            // 		res.push(`... ${data.length-6} items`)
            // 		res = `[\n${res.join(",\n")}\n]`
            // 	} else {
            // 		res = JSON.stringify(data, null, " ")
            // 	}

            // 	context.$log += `${res},\n`

            // })

            // context.$log +=`\n}`
        }
        return context;
    }
}
