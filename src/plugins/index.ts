import basicOperationsPlugin from './basic_operations_plugin';
import graphTransformerPlugin from './graph_transformer_plugin';
import { Plugin } from '../types';

const plugins: Plugin[] = [basicOperationsPlugin, graphTransformerPlugin];

export default plugins;
