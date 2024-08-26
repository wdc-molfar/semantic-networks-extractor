import fs from 'fs';
import YAML from 'js-yaml';
import data from './example.json';
import { SemNetExtractor } from './src';

const yaml = fs.readFileSync('./script.yaml', 'utf-8');

const script = YAML.load(yaml.replace(/\t/gm, ' ')) as Record<string, any>[];

const extractor = new SemNetExtractor();

const run = async () => {
    const context = await extractor.execute(script, { data });

    //console.log(context.output)

    const output_path = './output.json';
    fs.writeFileSync(output_path, JSON.stringify(context, null, 2));

    console.log(`All context written to ${output_path}`);
};

run().catch((e) => console.error(e));
