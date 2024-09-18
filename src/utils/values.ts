import { get, isArray, isObject, isString, keys, isUndefined } from 'lodash';
import { Context } from '../types';

export type VariableNameType = { $: string } | undefined;

export const resolveValue = <T>(
    variable: VariableNameType,
    context: Context,
    defaultValue?: T
) => {
    if (isUndefined(variable)) return;

    if (variable && variable.$) {
        let res = get(context, variable.$);

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
            const resolvedValue = resolveValues((value as any)[key], context);
            if (
                resolvedValue === undefined &&
                (value as any)[key] !== undefined &&
                '$' in (value as any)[key]
            ) {
                const reference = (value as any)[key].$ as string;
                Object.defineProperty(value, key, {
                    get() {
                        return context[reference];
                    },
                });
            } else if ((value as any)[key] !== resolvedValue)
                (value as any)[key] = resolvedValue;
        });
        return value;
    }

    return value;
};

export const resolveCommand = resolveValues;
