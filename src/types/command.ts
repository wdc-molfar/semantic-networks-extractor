import { Context } from './context';

export type CommandFunction = (
    command: any,
    context: Context,
    sender?: any
) => Promise<Context>;

export type Command =
    | {
          name: string[];
          _execute: CommandFunction;
      }
    | CommandFunction;
