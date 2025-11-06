#!/usr/bin/env python3
"""
🌌 Laniakea Protocol v0.0.02 - Unified Startup Script
اسکریپت راه‌اندازی یکپارچه و خودکار

این اسکریپت تمام مراحل لازم برای راه‌اندازی پروتکل را انجام می‌دهد:
- بررسی پیش‌نیازها
- نصب وابستگی‌ها
- پیکربندی اولیه
- راه‌اندازی سیستم
- مانیتورینگ health
"""

import os
import sys
import subprocess
import asyncio
import time
import signal
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('startup.log')
    ]
)
logger = logging.getLogger(__name__)


class LaniakeaStarter:
    """کلاس راه‌انداز پروتکل Laniakea"""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent.absolute()
        self.config_file = self.project_root / "config.yaml"
        self.env_file = self.project_root / ".env"
        self.requirements_file = self.project_root / "requirements_unified.txt"
        
        # Runtime options
        self.node_id = None
        self.port = 8000
        self.host = "0.0.0.0"
        self.environment = "production"
        self.enable_enhanced = True
        self.auto_install = False
        self.dev_mode = False
        
        # Process management
        self.processes: List[subprocess.Popen] = []
        self.running = True
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """مدیریت سیگنال‌های سیستم"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        self._cleanup_processes()
        sys.exit(0)
    
    def _cleanup_processes(self):
        """پاکسازی فرآیندهای در حال اجرا"""
        for process in self.processes:
            if process.poll() is None:
                logger.info(f"Terminating process {process.pid}")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def check_python_version(self) -> bool:
        """بررسی نسخه پایتون"""
        logger.info(f"Python version: {self.python_version}")
        
        if self.python_version < (3, 11):
            logger.error("Python 3.11 or higher is required")
            return False
        
        logger.info("✅ Python version check passed")
        return True
    
    def check_system_requirements(self) -> bool:
        """بررسی پیش‌نیازهای سیستم"""
        logger.info("Checking system requirements...")
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            if available_gb < 2:
                logger.warning(f"Low memory available: {available_gb:.1f}GB (recommended: 4GB+)")
            else:
                logger.info(f"✅ Memory available: {available_gb:.1f}GB")
        except ImportError:
            logger.warning("psutil not available, skipping memory check")
        
        # Check disk space
        disk_usage = self.project_root.statvfs(self.project_root)
        available_gb = (disk_usage.f_frsize * disk_usage.f_bavail) / (1024**3)
        
        if available_gb < 5:
            logger.warning(f"Low disk space: {available_gb:.1f}GB (recommended: 20GB+)")
        else:
            logger.info(f"✅ Disk space available: {available_gb:.1f}GB")
        
        # Check network connectivity (optional)
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            logger.info("✅ Network connectivity OK")
        except OSError:
            logger.warning("Network connectivity issues detected")
        
        return True
    
    def install_dependencies(self) -> bool:
        """نصب وابستگی‌ها"""
        logger.info("Installing dependencies...")
        
        if not self.requirements_file.exists():
            logger.error(f"Requirements file not found: {self.requirements_file}")
            return False
        
        try:
            # Upgrade pip
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, cwd=self.project_root)
            
            # Install requirements
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)]
            if self.dev_mode:
                cmd.append("-e")
            
            result = subprocess.run(
                cmd,
                check=True,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def create_directories(self) -> bool:
        """ایجاد دایرکتوری‌های لازم"""
        logger.info("Creating necessary directories...")
        
        directories = [
            "data",
            "logs",
            "backups",
            "models",
            "cache",
            "profiles",
            "uploads",
            "temp"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                return False
        
        return True
    
    def create_config_file(self) -> bool:
        """ایجاد فایل کانفیگ"""
        if self.config_file.exists():
            logger.info("Configuration file already exists")
            return True
        
        logger.info("Creating default configuration file...")
        
        try:
            # Import config creation logic
            sys.path.insert(0, str(self.project_root))
            from config_unified import UnifiedConfig
            
            config = UnifiedConfig(
                config_file=str(self.config_file),
                environment=self.environment
            )
            
            # Update with runtime settings
            config.network.host = self.host
            config.network.port = self.port
            
            if self.dev_mode:
                config.monitoring.log_level = "DEBUG"
                config.network.reload = True
            
            config.save_config()
            logger.info("✅ Configuration file created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create config file: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """ایجاد فایل .env"""
        if self.env_file.exists():
            logger.info("Environment file already exists")
            return True
        
        logger.info("Creating environment file...")
        
        env_content = f"""# Laniakea Protocol Environment Configuration
# Generated automatically by start.py

# Network Configuration
HOST={self.host}
PORT={self.port}

# Node Configuration
NODE_ID={self.node_id or 'laniakea-node-001'}
IS_AUTHORITY=false

# Security (CHANGE THESE IN PRODUCTION)
JWT_SECRET_KEY=your-secret-key-change-this-{int(time.time())}
ENCRYPTION_KEY=your-encryption-key-change-this-{int(time.time())}

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here
COGNITIVE_MODEL=gpt-4

# Blockchain Configuration
BLOCK_TIME=20
BLOCK_REWARD=10.0

# Performance
AUTO_OPTIMIZE=true
TARGET_EFFICIENCY=0.85

# Development
DEV_MODE={'true' if self.dev_mode else 'false'}
DEBUG={'true' if self.dev_mode else 'false'}

# Logging
LOG_LEVEL={'DEBUG' if self.dev_mode else 'INFO'}
LOG_FILE=./logs/laniakea.log
"""
        
        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            logger.info("✅ Environment file created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create env file: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """اجرای بررسی سلامت"""
        logger.info("Running health check...")
        
        try:
            # Import and run health check
            sys.path.insert(0, str(self.project_root))
            from main_unified import LaniakeaProtocol
            
            # Create protocol instance (without starting)
            protocol = LaniakeaProtocol(
                node_id=self.node_id or "health-check",
                port=self.port + 1,  # Use different port for health check
                enable_enhanced=self.enable_enhanced
            )
            
            # Test basic functionality
            logger.info("✅ Protocol initialization successful")
            logger.info("✅ Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def start_protocol(self) -> bool:
        """راه‌اندازی پروتکل"""
        logger.info("Starting Laniakea Protocol...")
        
        try:
            # Prepare command
            cmd = [
                sys.executable, "main_unified.py",
                "--node-id", self.node_id or "laniakea-node-001",
                "--port", str(self.port),
                "--host", self.host
            ]
            
            if not self.enable_enhanced:
                cmd.append("--disable-enhanced")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes.append(process)
            
            logger.info(f"✅ Protocol started (PID: {process.pid})")
            logger.info(f"📡 Dashboard available at: http://{self.host}:{self.port}")
            logger.info(f"📚 API docs available at: http://{self.host}:{self.port}/docs")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start protocol: {e}")
            return False
    
    def monitor_process(self, process: subprocess.Popen) -> None:
        """مانیتورینگ فرآیند در حال اجرا"""
        logger.info("Starting process monitoring...")
        
        while self.running and process.poll() is None:
            try:
                # Read output
                line = process.stdout.readline()
                if line:
                    print(line.strip())
                
                # Check if process is still responsive
                if not self.dev_mode:
                    # In production, we could add health checks here
                    pass
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                break
        
        # Check exit code
        if process.poll() is not None:
            exit_code = process.returncode
            if exit_code != 0:
                logger.error(f"Process exited with code: {exit_code}")
            else:
                logger.info("Process exited normally")
    
    def run_interactive_setup(self) -> bool:
        """راه‌اندازی تعاملی"""
        logger.info("Starting interactive setup...")
        
        print("\n🌌 Welcome to Laniakea Protocol v0.0.02 Setup")
        print("=" * 50)
        
        # Node ID
        node_id = input("Enter node ID (default: laniakea-node-001): ").strip()
        self.node_id = node_id or "laniakea-node-001"
        
        # Port
        port_input = input("Enter port (default: 8000): ").strip()
        try:
            self.port = int(port_input) if port_input else 8000
        except ValueError:
            logger.warning("Invalid port, using default: 8000")
            self.port = 8000
        
        # Host
        host_input = input("Enter host (default: 0.0.0.0): ").strip()
        self.host = host_input or "0.0.0.0"
        
        # Environment
        env_input = input("Environment (development/staging/production, default: production): ").strip().lower()
        environment_map = {
            "dev": "development",
            "development": "development",
            "stage": "staging",
            "staging": "staging",
            "prod": "production",
            "production": "production"
        }
        self.environment = environment_map.get(env_input, "production")
        
        # Enhanced features
        enhanced_input = input("Enable enhanced features? (y/n, default: y): ").strip().lower()
        self.enable_enhanced = enhanced_input != "n"
        
        # Development mode
        dev_input = input("Development mode? (y/n, default: n): ").strip().lower()
        self.dev_mode = dev_input == "y"
        
        # Auto install
        auto_input = input("Auto-install dependencies? (y/n, default: y): ").strip().lower()
        self.auto_install = auto_input != "n"
        
        print("\nConfiguration Summary:")
        print(f"  Node ID: {self.node_id}")
        print(f"  Host:Port: {self.host}:{self.port}")
        print(f"  Environment: {self.environment}")
        print(f"  Enhanced Features: {'Yes' if self.enable_enhanced else 'No'}")
        print(f"  Development Mode: {'Yes' if self.dev_mode else 'No'}")
        print(f"  Auto-Install: {'Yes' if self.auto_install else 'No'}")
        
        confirm = input("\nProceed with this configuration? (y/n): ").strip().lower()
        return confirm == "y"
    
    def run_startup_sequence(self) -> bool:
        """اجرای توالی راه‌اندازی"""
        logger.info("Starting Laniakea Protocol startup sequence...")
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("System Requirements Check", self.check_system_requirements),
        ]
        
        # Add optional steps
        if self.auto_install:
            steps.append(("Dependency Installation", self.install_dependencies))
        
        steps.extend([
            ("Directory Creation", self.create_directories),
            ("Config File Creation", self.create_config_file),
            ("Environment File Creation", self.create_env_file),
            ("Health Check", self.run_health_check),
        ])
        
        for step_name, step_func in steps:
            logger.info(f"Running: {step_name}")
            if not step_func():
                logger.error(f"Failed at step: {step_name}")
                return False
            logger.info(f"✅ Completed: {step_name}")
        
        return True
    
    def start(self) -> None:
        """شروع اصلی"""
        logger.info("🌌 Laniakea Protocol v0.0.02 Unified Starter")
        
        # Run startup sequence
        if not self.run_startup_sequence():
            logger.error("Startup sequence failed")
            sys.exit(1)
        
        # Start protocol
        if not self.start_protocol():
            logger.error("Failed to start protocol")
            sys.exit(1)
        
        # Monitor the process
        if self.processes:
            self.monitor_process(self.processes[0])
        
        logger.info("Startup process completed")


def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(
        description="Laniakea Protocol v0.0.02 Unified Starter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py                    # Interactive setup
  python start.py --node-id node1    # Quick start with node ID
  python start.py --port 8080        # Custom port
  python start.py --dev              # Development mode
  python start.py --no-enhanced      # Basic mode only
        """
    )
    
    parser.add_argument("--node-id", help="Node identifier")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--environment", choices=["development", "staging", "production"], 
                       default="production", help="Environment (default: production)")
    parser.add_argument("--no-enhanced", action="store_true", help="Disable enhanced features")
    parser.add_argument("--auto-install", action="store_true", help="Auto-install dependencies")
    parser.add_argument("--dev", action="store_true", help="Development mode")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--env", help="Environment file path")
    parser.add_argument("--interactive", action="store_true", help="Interactive setup")
    
    args = parser.parse_args()
    
    # Create starter instance
    starter = LaniakeaStarter()
    
    # Apply command line arguments
    starter.node_id = args.node_id
    starter.port = args.port
    starter.host = args.host
    starter.environment = args.environment
    starter.enable_enhanced = not args.no_enhanced
    starter.auto_install = args.auto_install
    starter.dev_mode = args.dev
    
    if args.config:
        starter.config_file = Path(args.config)
    
    if args.env:
        starter.env_file = Path(args.env)
    
    # Interactive mode if requested or no arguments provided
    if args.interactive or not any([args.node_id, args.port != 8000, args.config, args.env]):
        if not starter.run_interactive_setup():
            print("Setup cancelled")
            sys.exit(0)
    
    # Start the protocol
    try:
        starter.start()
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
        starter._cleanup_processes()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        starter._cleanup_processes()
        sys.exit(1)


if __name__ == "__main__":
    main()