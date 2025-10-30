#!/usr/bin/env node
/**
 * JavaScript AST Parser using Babel
 * Parses ES6+ JavaScript files and generates AST in XML format
 */

const fs = require('fs');
const path = require('path');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

/**
 * Parse JavaScript file and generate AST
 * @param {string} filePath - Path to JavaScript file
 * @param {string} outputPath - Path to output XML file
 */
function parseJavaScriptToAST(filePath, outputPath) {
  try {
    // Read source code
    const sourceCode = fs.readFileSync(filePath, 'utf-8');
    
    // Parse with Babel
    const ast = parser.parse(sourceCode, {
      sourceType: 'module',
      plugins: [
        'jsx',
        'classProperties',
        'decorators-legacy',
        'asyncGenerators',
        'bigInt',
        'dynamicImport',
        'nullishCoalescingOperator',
        'optionalChaining'
      ]
    });
    
    // Extract metadata
    const metadata = {
      imports: [],
      exports: [],
      classes: [],
      functions: [],
      variables: []
    };
    
    // Traverse AST to extract information
    traverse(ast, {
      ImportDeclaration(path) {
        const importInfo = {
          source: path.node.source.value,
          specifiers: path.node.specifiers.map(spec => {
            if (spec.type === 'ImportDefaultSpecifier') {
              return { type: 'default', local: spec.local.name };
            } else if (spec.type === 'ImportSpecifier') {
              return { 
                type: 'named', 
                imported: spec.imported.name, 
                local: spec.local.name 
              };
            }
            return null;
          }).filter(Boolean)
        };
        metadata.imports.push(importInfo);
      },
      
      ExportDefaultDeclaration(path) {
        metadata.exports.push({
          type: 'default',
          name: path.node.declaration.id?.name || 'anonymous'
        });
      },
      
      ExportNamedDeclaration(path) {
        if (path.node.declaration) {
          if (path.node.declaration.type === 'ClassDeclaration') {
            metadata.exports.push({
              type: 'class',
              name: path.node.declaration.id.name
            });
          } else if (path.node.declaration.type === 'FunctionDeclaration') {
            metadata.exports.push({
              type: 'function',
              name: path.node.declaration.id.name
            });
          }
        }
      },
      
      ClassDeclaration(path) {
        const classInfo = {
          name: path.node.id.name,
          superClass: path.node.superClass?.name || null,
          methods: []
        };
        
        path.node.body.body.forEach(member => {
          if (member.type === 'ClassMethod') {
            classInfo.methods.push({
              name: member.key.name,
              kind: member.kind, // 'constructor', 'method', 'get', 'set'
              async: member.async,
              static: member.static,
              params: member.params.map(p => p.name || p.type)
            });
          } else if (member.type === 'ClassProperty') {
            // Class properties
            if (!classInfo.properties) {
              classInfo.properties = [];
            }
            classInfo.properties.push({
              name: member.key.name,
              static: member.static
            });
          }
        });
        
        metadata.classes.push(classInfo);
      },
      
      FunctionDeclaration(path) {
        // Skip if it's inside a class (already captured)
        if (path.parent.type === 'Program' || path.parent.type === 'ExportNamedDeclaration') {
          metadata.functions.push({
            name: path.node.id.name,
            async: path.node.async,
            params: path.node.params.map(p => p.name || p.type)
          });
        }
      }
    });
    
    // Generate XML output
    const xml = generateXML(metadata, path.basename(filePath));
    
    // Write to output file
    fs.writeFileSync(outputPath, xml, 'utf-8');
    
    console.log(`AST generated successfully: ${outputPath}`);
    return true;
  } catch (error) {
    console.error(`Failed to parse ${filePath}:`, error.message);
    return false;
  }
}

/**
 * Generate XML from metadata
 * @param {object} metadata - Extracted metadata
 * @param {string} fileName - Original file name
 * @returns {string} XML string
 */
function generateXML(metadata, fileName) {
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += `<JavaScriptFile name="${fileName}">\n`;
  
  // Imports
  if (metadata.imports.length > 0) {
    xml += '  <Imports>\n';
    metadata.imports.forEach(imp => {
      xml += `    <Import source="${escapeXml(imp.source)}">\n`;
      imp.specifiers.forEach(spec => {
        xml += `      <Specifier type="${spec.type}" imported="${escapeXml(spec.imported || spec.local)}" local="${escapeXml(spec.local)}" />\n`;
      });
      xml += '    </Import>\n';
    });
    xml += '  </Imports>\n';
  }
  
  // Exports
  if (metadata.exports.length > 0) {
    xml += '  <Exports>\n';
    metadata.exports.forEach(exp => {
      xml += `    <Export type="${exp.type}" name="${escapeXml(exp.name)}" />\n`;
    });
    xml += '  </Exports>\n';
  }
  
  // Classes
  if (metadata.classes.length > 0) {
    xml += '  <Classes>\n';
    metadata.classes.forEach(cls => {
      xml += `    <Class name="${escapeXml(cls.name)}"`;
      if (cls.superClass) {
        xml += ` superClass="${escapeXml(cls.superClass)}"`;
      }
      xml += '>\n';
      
      // Properties
      if (cls.properties && cls.properties.length > 0) {
        xml += '      <Properties>\n';
        cls.properties.forEach(prop => {
          xml += `        <Property name="${escapeXml(prop.name)}" static="${prop.static}" />\n`;
        });
        xml += '      </Properties>\n';
      }
      
      // Methods
      if (cls.methods.length > 0) {
        xml += '      <Methods>\n';
        cls.methods.forEach(method => {
          xml += `        <Method name="${escapeXml(method.name)}" kind="${method.kind}" async="${method.async}" static="${method.static}">\n`;
          if (method.params.length > 0) {
            xml += '          <Parameters>\n';
            method.params.forEach(param => {
              xml += `            <Parameter name="${escapeXml(param)}" />\n`;
            });
            xml += '          </Parameters>\n';
          }
          xml += '        </Method>\n';
        });
        xml += '      </Methods>\n';
      }
      
      xml += '    </Class>\n';
    });
    xml += '  </Classes>\n';
  }
  
  // Functions
  if (metadata.functions.length > 0) {
    xml += '  <Functions>\n';
    metadata.functions.forEach(func => {
      xml += `    <Function name="${escapeXml(func.name)}" async="${func.async}">\n`;
      if (func.params.length > 0) {
        xml += '      <Parameters>\n';
        func.params.forEach(param => {
          xml += `        <Parameter name="${escapeXml(param)}" />\n`;
        });
        xml += '      </Parameters>\n';
      }
      xml += '    </Function>\n';
    });
    xml += '  </Functions>\n';
  }
  
  xml += '</JavaScriptFile>\n';
  return xml;
}

/**
 * Escape XML special characters
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
function escapeXml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

// Command line interface
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.error('Usage: node js_ast_parser.js <input.js> <output.xml>');
    process.exit(1);
  }
  
  const inputFile = args[0];
  const outputFile = args[1];
  
  if (!fs.existsSync(inputFile)) {
    console.error(`Input file not found: ${inputFile}`);
    process.exit(1);
  }
  
  const success = parseJavaScriptToAST(inputFile, outputFile);
  process.exit(success ? 0 : 1);
}

module.exports = { parseJavaScriptToAST };
