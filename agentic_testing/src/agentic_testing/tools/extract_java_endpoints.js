// extract_java_endpoints.js
// Run with: node extract_java_endpoints.js

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Get the project root directory (4 levels up from this file)
const projectRoot = path.resolve(__dirname, '../../../..');
const BACKEND_DIR = path.join(projectRoot, 'testing_automation/backend/src/main/java');
const OUT_DIR = path.join(projectRoot, 'features', 'meta_data');
const OUT_ENDPOINTS = path.join(OUT_DIR, 'endpoints_babel.json');

function extractEndpointsFromJavaFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const endpoints = [];
  
  // Split content into lines for easier processing
  const lines = content.split('\n');
  
  let classRequestMapping = '';
  
  // First pass: find class-level @RequestMapping
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const classRequestMappingMatch = line.match(/@RequestMapping\s*\(\s*["']([^"']+)["']/);
    if (classRequestMappingMatch) {
      classRequestMapping = classRequestMappingMatch[1];
      break;
    }
  }
  
  // Second pass: find method-level annotations
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Method-level annotations
    const methodPatterns = [
      { pattern: /@GetMapping\s*\(\s*["']([^"']+)["']/, method: 'GET' },
      { pattern: /@PostMapping\s*\(\s*["']([^"']+)["']/, method: 'POST' },
      { pattern: /@PutMapping\s*\(\s*["']([^"']+)["']/, method: 'PUT' },
      { pattern: /@DeleteMapping\s*\(\s*["']([^"']+)["']/, method: 'DELETE' },
      { pattern: /@PatchMapping\s*\(\s*["']([^"']+)["']/, method: 'PATCH' },
    ];
    
    for (const { pattern, method } of methodPatterns) {
      const match = line.match(pattern);
      if (match) {
        let endpointPath = match[1];
        
        // Combine with class-level @RequestMapping if it exists
        if (classRequestMapping) {
          // Ensure proper path joining (avoid double slashes)
          if (endpointPath.startsWith('/')) {
            endpointPath = classRequestMapping + endpointPath;
          } else {
            endpointPath = classRequestMapping + '/' + endpointPath;
          }
        }
        
        endpoints.push({
          method: method,
          path: endpointPath,
          file: filePath,
          line: i + 1,
          type: 'java-backend'
        });
      }
    }
  }
  
  return endpoints;
}

function main() {
  if (!fs.existsSync(OUT_DIR)) {
    fs.mkdirSync(OUT_DIR, { recursive: true });
  }
  
  // Find all Java files in the backend
  const javaFiles = glob.sync(`${BACKEND_DIR}/**/*.java`);
  
  let allEndpoints = [];
  
  for (const file of javaFiles) {
    try {
      const endpoints = extractEndpointsFromJavaFile(file);
      allEndpoints.push(...endpoints);
      console.log(`Processed ${file}: found ${endpoints.length} endpoints`);
    } catch (error) {
      console.warn(`Error processing ${file}: ${error.message}`);
    }
  }
  
  // Read existing endpoints from endpoints_babel.json
  let existingEndpoints = [];
  if (fs.existsSync(OUT_ENDPOINTS)) {
    try {
      const existingContent = fs.readFileSync(OUT_ENDPOINTS, 'utf8');
      existingEndpoints = JSON.parse(existingContent);
      console.log(`Found ${existingEndpoints.length} existing endpoints in ${OUT_ENDPOINTS}`);
    } catch (error) {
      console.warn(`Error reading existing endpoints: ${error.message}`);
      existingEndpoints = [];
    }
  }
  
  // Combine existing and new endpoints
  const combinedEndpoints = [...existingEndpoints];
  
  // Add new Java endpoints, ensuring uniqueness
  const seen = new Set();
  
  // Add existing endpoints to seen set
  for (const endpoint of existingEndpoints) {
    const key = `${endpoint.method}|${endpoint.path}`;
    seen.add(key);
  }
  
  // Add new Java endpoints
  for (const endpoint of allEndpoints) {
    const key = `${endpoint.method}|${endpoint.path}`;
    if (!seen.has(key)) {
      seen.add(key);
      combinedEndpoints.push({
        method: endpoint.method,
        path: endpoint.path
      });
    }
  }
  
  // Write combined endpoints back to the same file
  fs.writeFileSync(OUT_ENDPOINTS, JSON.stringify(combinedEndpoints, null, 2));
  
  console.log(`\nExtracted ${allEndpoints.length} new Java backend endpoints:`);
  allEndpoints.forEach(endpoint => {
    console.log(`  ${endpoint.method} ${endpoint.path}`);
  });
  
  console.log(`\nTotal unique endpoints in ${OUT_ENDPOINTS}: ${combinedEndpoints.length}`);
  console.log(`Results appended to: ${OUT_ENDPOINTS}`);
}

main(); 