// extract_all_metadata-babel.js
// Run with: node extract_all_metadata-babel.js

const fs = require('fs');
const path = require('path');
const glob = require('glob');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

// Get the project root directory (4 levels up from this file)
const projectRoot = path.resolve(__dirname, '../../../..');
const SRC_DIR = path.join(projectRoot, 'testing_automation/src');
const OUT_DIR = path.join(projectRoot, 'features', 'meta_data');
const OUT_MESSAGES = path.join(OUT_DIR, 'extracted_messages_babel.json');
const OUT_LOCATORS = path.join(OUT_DIR, 'locators_babel.json');
const OUT_ENDPOINTS = path.join(OUT_DIR, 'endpoints_babel.json');
const OUT_UI = path.join(OUT_DIR, 'ui_endpoints_babel.json');

const API_PREFIXES = process.env.API_PREFIXES ? process.env.API_PREFIXES.split(',') : ['/api/', '/auth/', '/v1/', '/v2/'];
const FILE_EXTENSIONS = ['.js', '.jsx', '.ts', '.tsx'];

function isApiUrl(url) {
  return API_PREFIXES.some(prefix => url.startsWith(prefix));
}

function parseFile(filePath) {
  const code = fs.readFileSync(filePath, 'utf8');
  let ast;
  try {
    ast = parser.parse(code, {
      sourceType: 'unambiguous',
      plugins: [
        'jsx',
        'typescript',
        'classProperties',
        'objectRestSpread',
        'optionalChaining',
        'decorators-legacy',
      ],
    });
  } catch (e) {
    console.warn(`Failed to parse ${filePath}: ${e.message}`);
    return null;
  }
  return ast;
}

function extractFromAst(ast, filePath) {
  const messages = [];
  const locators = [];
  const endpoints = [];
  const uiRoutes = [];

  traverse(ast, {
    // --- Messages ---
    CallExpression(path) {
      const { callee, arguments: args } = path.node;
      // toast.*('message')
      if (
        callee.type === 'MemberExpression' &&
        callee.object.name === 'toast' &&
        ['error', 'success', 'info', 'warning'].includes(callee.property.name)
      ) {
        if (args[0] && args[0].type === 'StringLiteral') {
          messages.push({
            message: args[0].value,
            type: `toast.${callee.property.name}`,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // toast({ title: '...', description: '...' })
      if (
        callee.type === 'Identifier' &&
        callee.name === 'toast' &&
        args[0] && args[0].type === 'ObjectExpression'
      ) {
        const objProps = args[0].properties;
        for (const prop of objProps) {
          let keyName = null;
          if (prop.key.type === 'Identifier') keyName = prop.key.name;
          else if (prop.key.type === 'StringLiteral') keyName = prop.key.value;
          // Debug log for all toast object properties
          if (keyName && prop.value.type === 'StringLiteral') {
            console.log(`[DEBUG] toast property in ${filePath} line ${path.node.loc.start.line}: ${keyName} = ${prop.value.value}`);
          }
          if (
            keyName === 'title' &&
            prop.value.type === 'StringLiteral'
          ) {
            messages.push({
              message: prop.value.value,
              type: 'toast-title',
              file: filePath,
              line: path.node.loc.start.line,
            });
          }
          if (
            keyName === 'description' &&
            prop.value.type === 'StringLiteral'
          ) {
            messages.push({
              message: prop.value.value,
              type: 'toast-desc',
              file: filePath,
              line: path.node.loc.start.line,
            });
          }
        }
      }
      // t('message')
      if (callee.type === 'Identifier' && callee.name === 't') {
        if (args[0] && args[0].type === 'StringLiteral') {
          messages.push({
            message: args[0].value,
            type: 'i18n',
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // setError('message')
      if (callee.type === 'Identifier' && callee.name === 'setError') {
        if (args[0] && args[0].type === 'StringLiteral') {
          messages.push({
            message: args[0].value,
            type: 'setError',
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // alert('message')
      if (callee.type === 'Identifier' && callee.name === 'alert') {
        if (args[0] && args[0].type === 'StringLiteral') {
          messages.push({
            message: args[0].value,
            type: 'alert',
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // throw new Error('message')
      if (
        callee.type === 'MemberExpression' &&
        callee.object.type === 'Identifier' &&
        callee.object.name === 'Error' &&
        callee.property.name === 'call'
      ) {
        // skip
      } else if (
        callee.type === 'Identifier' &&
        callee.name === 'Error' &&
        path.parent.type === 'NewExpression' &&
        args[0] && args[0].type === 'StringLiteral'
      ) {
        messages.push({
          message: args[0].value,
          type: 'throwError',
          file: filePath,
          line: path.node.loc.start.line,
        });
      }
      // console.log/warn/error('message')
      if (
        callee.type === 'MemberExpression' &&
        callee.object.name === 'console' &&
        ['log', 'warn', 'error'].includes(callee.property.name)
      ) {
        if (args[0] && args[0].type === 'StringLiteral') {
          messages.push({
            message: args[0].value,
            type: `console.${callee.property.name}`,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
    },
    // --- Locators (JSX attributes) ---
    JSXAttribute(path) {
      const { name, value } = path.node;
      if (!value || value.type !== 'StringLiteral') return;
      const attrName = name.name;
      const attrValue = value.value;
      // Add support for data-testid, data-qa, aria-* attributes
      if (
        /^(id|data-(testid|test|qa)|aria-[\w-]+|placeholder|type)$/.test(attrName)
      ) {
        locators.push({
          key: attrValue,
          strategy: attrName,
          by: attrName,
          selector: `[${attrName}='${attrValue}']`,
          value: attrValue,
          file: filePath,
          line: path.node.loc.start.line,
        });
      }
    },
    // --- Locators (JSXOpeningElement for spread/implicit attributes) ---
    JSXOpeningElement(path) {
      // For future: could extract from spread attributes if needed
      // --- UI Routes (React Router) ---
      if (path.node.name.name === 'Route') {
        const pathAttr = path.node.attributes.find(
          attr => attr.name && attr.name.name === 'path' && attr.value.type === 'StringLiteral'
        );
        if (pathAttr) {
          uiRoutes.push({
            path: pathAttr.value.value,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
    },
    // --- React Router v6 useRoutes array support ---
    VariableDeclarator(path) {
      // Looks for: const routes = [ ... ]; useRoutes(routes)
      if (
        path.node.init &&
        path.node.init.type === 'ArrayExpression' &&
        path.node.id.name &&
        /routes?/i.test(path.node.id.name)
      ) {
        for (const el of path.node.init.elements) {
          if (
            el &&
            el.type === 'ObjectExpression'
          ) {
            const pathProp = el.properties.find(
              p => ((p.key && (p.key.name === 'path' || p.key.value === 'path')) && p.value.type === 'StringLiteral')
            );
            if (pathProp) {
              uiRoutes.push({
                path: pathProp.value.value,
                file: filePath,
                line: el.loc ? el.loc.start.line : path.node.loc.start.line,
              });
            }
          }
        }
      }
    },
    // --- API Endpoints ---
    CallExpression(path) {
      const { callee, arguments: args } = path.node;
      // this.request('/api/endpoint', { method: 'POST' })
      if (
        (callee.type === 'MemberExpression' && callee.property.name === 'request') ||
        (callee.type === 'Identifier' && callee.name === 'request')
      ) {
        if (args[0] && args[0].type === 'StringLiteral' && isApiUrl(args[0].value)) {
          let method = 'GET';
          if (
            args[1] && args[1].type === 'ObjectExpression'
          ) {
            const methodProp = args[1].properties.find(
              p => p.key && p.key.name === 'method' && p.value.type === 'StringLiteral'
            );
            if (methodProp) method = methodProp.value.value;
          }
          endpoints.push({
            method: method.toUpperCase(),
            path: args[0].value,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // fetch('/api/endpoint', ...)
      if (callee.type === 'Identifier' && callee.name === 'fetch') {
        if (args[0] && args[0].type === 'StringLiteral' && isApiUrl(args[0].value)) {
          endpoints.push({
            method: 'GET',
            path: args[0].value,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
      // axios.get/post/put/delete('/api/endpoint', ...)
      if (
        callee.type === 'MemberExpression' &&
        callee.object.name === 'axios' &&
        ['get', 'post', 'put', 'delete'].includes(callee.property.name)
      ) {
        if (args[0] && args[0].type === 'StringLiteral' && isApiUrl(args[0].value)) {
          endpoints.push({
            method: callee.property.name.toUpperCase(),
            path: args[0].value,
            file: filePath,
            line: path.node.loc.start.line,
          });
        }
      }
    },
  });

  return { messages, locators, endpoints, uiRoutes };
}

function dedupe(arr, keyFn) {
  const seen = new Set();
  return arr.filter(item => {
    const key = keyFn(item);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function main() {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
  // Exclude test and __tests__ folders from glob
  const files = glob.sync(`${SRC_DIR}/**/*.{js,jsx,ts,tsx}`, {
    ignore: [
      `${SRC_DIR}/test/**/*`,
      `${SRC_DIR}/**/test/**/*`,
      `${SRC_DIR}/__tests__/**/*`,
      `${SRC_DIR}/**/__tests__/**/*`,
    ]
  });
  let allMessages = [], allLocators = [], allEndpoints = [], allUI = [];
  for (const file of files) {
    const ast = parseFile(file);
    if (!ast) continue;
    const { messages, locators, endpoints, uiRoutes } = extractFromAst(ast, file);
    allMessages.push(...messages);
    allLocators.push(...locators);
    allEndpoints.push(...endpoints);
    allUI.push(...uiRoutes);
  }
  // Deduplicate
  allMessages = dedupe(allMessages, m => `${m.message}|${m.type}`);
  allLocators = dedupe(allLocators, l => `${l.key}|${l.strategy}|${l.by}|${l.selector}|${l.value}`);
  allEndpoints = dedupe(allEndpoints, e => `${e.method}|${e.path}`);
  allUI = dedupe(allUI, u => u.path);
  // Write
  fs.writeFileSync(OUT_LOCATORS, JSON.stringify(allLocators.map(l => ({ key: l.key, strategy: l.strategy, by: l.by, selector: l.selector, value: l.value })), null, 2));
  fs.writeFileSync(OUT_ENDPOINTS, JSON.stringify(allEndpoints.map(e => ({ method: e.method, path: e.path })), null, 2));
  fs.writeFileSync(OUT_UI, JSON.stringify(allUI.map(u => ({ path: u.path })), null, 2));
  console.log(`(Babel) Extracted ${allLocators.length} locators, ${allEndpoints.length} endpoints, ${allUI.length} UI routes. (Messages are extracted by Python.)`);
}

main(); 