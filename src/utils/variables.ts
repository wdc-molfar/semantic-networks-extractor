const reservedKeywordsAndGlobals = [
    'true',
    'false',
    'null',
    'in',
    'new',
    'return',
    'this',
    'var',
    'let',
    'const',
    ...Object.getOwnPropertyNames(global),
];

export const resolveContextVariables = (
    condition: string,
    contextName = 'context'
) => {
    return condition.replace(
        /([a-zA-Z_]\w*(?:\.\w+|\["[^"]*"\]|\['[^']*'\])*)/g,
        (match) => {
            // check if the match is a valid literal, a reserved keyword or global object, we skip replacement for those
            if (
                reservedKeywordsAndGlobals.includes(match.split(/[\.\[]/)[0]) ||
                !isNaN(+match) ||
                /^["'].*["']$/.test(match)
            ) {
                return match; // it's a literal or a keyword, don't replace it
            }

            // otherwise, replace it with a reference from the context
            return `${contextName}.${match}`;
        }
    );
};
