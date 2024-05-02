const { get, isArray, isObject, isString, keys, isUndefined } = require("lodash")

const resolveValue = (variable, context, defaultValue) => {
    if(isUndefined(variable)) return

    if(variable && variable.$){
        let res = get(context, variable.$)

        return (isUndefined(res)) ? defaultValue : res
    }

    return variable
}

const resolveValues = (variable, context) => {
    variable = resolveValue(variable, context)

    if(isArray(variable)){
        variable = variable.map( d => resolveValues(d, context))
        return variable
    }

    if(isObject(variable) && !isString(variable)){
        keys(variable).forEach( key => {
            variable[key] = resolveValues(variable[key], context)
        })
        return variable
    }

    return variable
}

module.exports = {
    resolveValue,
    resolveCommand: resolveValues
}
