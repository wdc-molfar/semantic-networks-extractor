import { Plugin } from './plugin';
import { Context } from './context';

export interface Executor {
    use(plugins: Plugin | Plugin[]): void;

    register(plugins: Plugin | Plugin[]): void;

    executeOnce(
        command: Record<string, any>,
        context: Context,
        sender?: any
    ): Promise<Context>;

    execute(
        script: string | Record<string, any>[],
        context: Context
    ): Promise<Context>;
}
