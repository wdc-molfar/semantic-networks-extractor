import { Executor } from './executor';
import { Command } from './command';

export type Plugin = {
    register?: (executor: Executor) => void;
    commands: Command[];
    close?: () => Promise<void>;
};
