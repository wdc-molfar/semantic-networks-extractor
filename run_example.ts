import fs from 'fs';
import YAML from 'js-yaml';
import { SemNetExtractor } from './src';

const exampleId = 'relations';

const data = JSON.parse(
    fs.readFileSync(`./examples/${exampleId}/input.json`, 'utf-8')
);
const yaml = fs.readFileSync(`./examples/${exampleId}/script.yaml`, 'utf-8');

const script = YAML.load(yaml.replace(/\t/gm, ' ')) as Record<string, any>[];

const extractor = new SemNetExtractor();

const run = async () => {
    //fetch('http://localhost:3001/stanza', { method: 'POST', body: JSON.stringify({ text: 'The President signed the new agreement, while the secretary organized meetings.' }), headers: { "Content-Type": "application/json", }}).then(res => res.json()).then(({response}) => fs.writeFileSync('./input.json', JSON.stringify(response, null, 2))).then(() => console.log('Done!'))

    const context = await extractor.execute(script, { data });

    //console.log(context.output)

    const output_path = './output.json';
    fs.writeFileSync(output_path, JSON.stringify(context, null, 2));

    console.log(`All context written to ${output_path}`);
};

run().catch((e) => console.error(e));
