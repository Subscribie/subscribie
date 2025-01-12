import fs from 'fs'
import YAML from 'yaml'

const file = fs.readFileSync('./settings.yaml', 'utf8')

let settings = YAML.parse(file)

console.log(settings)

