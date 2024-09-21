import { get, isArray, isObject, isString, keys, isUndefined } from 'lodash';
import { Context } from '../types';

export type VariableNameType = { $: string } | undefined;

export const resolveValue = <T>(
    variable: VariableNameType,
    context: Context,
    defaultValue?: T
) => {
    if (isUndefined(variable)) return undefined;

    if (variable?.$) {
        const res = get(context, variable.$);

        return isUndefined(res) ? defaultValue : res;
    }

    return variable;
};

export const resolveValues = (
    variable: VariableNameType,
    context: Context
): any => {
    if (variable === undefined) return undefined;
    const value = resolveValue(variable, context);

    if (isArray(value)) {
        return value.map((d: VariableNameType) => resolveValues(d, context));
    }

    if (isObject(value) && !isString(value)) {
        keys(value).forEach((key) => {
            if (isObject((value as any)[key]) && '$' in (value as any)[key]) {
                const reference = (value as any)[key].$ as string;
                Object.defineProperty(value, key, {
                    get() {
                        return context[reference];
                    },
                });
            }
        });
        return value;
    }

    return value;
};

export const resolveCommand = resolveValues;
