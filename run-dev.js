const { spawn } = require('child_process');
const path = require('path');

// Define colors for different processes
const colors = {
  frontend: '\x1b[36m', // Cyan
  backend: '\x1b[32m',  // Green
  reset: '\x1b[0m'      // Reset
};

// Function to run a command
function runCommand(command, args, name) {
  const color = colors[name] || colors.reset;
  
  console.log(`${color}Starting ${name}...${colors.reset}`);
  
  const process = spawn(command, args, { 
    shell: true,
    stdio: 'pipe',
    cwd: path.resolve(__dirname)
  });
  
  process.stdout.on('data', (data) => {
    console.log(`${color}[${name}] ${data.toString().trim()}${colors.reset}`);
  });
  
  process.stderr.on('data', (data) => {
    console.error(`${color}[${name}] ${data.toString().trim()}${colors.reset}`);
  });
  
  process.on('close', (code) => {
    console.log(`${color}${name} process exited with code ${code}${colors.reset}`);
  });
  
  return process;
}

// Start frontend (Next.js)
const frontend = runCommand('npm', ['run', 'dev'], 'frontend');

// Start backend (Python)
const backend = runCommand('python', ['-m', 'backend.main'], 'backend');

// Handle process termination
process.on('SIGINT', () => {
  console.log('\nGracefully shutting down...');
  frontend.kill();
  backend.kill();
  process.exit(0);
});