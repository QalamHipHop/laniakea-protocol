#!/usr/bin/env python3
"""
LaniakeA Protocol - Command Line Interface
Advanced CLI with intelligent command processing and developer mode
Version: 3.0.0
"""

import asyncio
import click
import sys
import os
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from laniakea.utils.logger import setup_logger, get_logger
from laniakea.utils.config import get_config
from laniakea.core.hypercube_blockchain import HypercubeBlockchain
from laniakea.intelligence.brain import CosmicBrainAI
from laniakea.network.api import create_app, run_server


# ASCII Art Banner
LANIAKEA_BANNER = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██╗      █████╗ ███╗   ██╗██╗ █████╗ ██╗  ██╗███████╗ █████╗     ║
║   ██║     ██╔══██╗████╗  ██║██║██╔══██╗██║ ██╔╝██╔════╝██╔══██╗    ║
║   ██║     ███████║██╔██╗ ██║██║███████║█████╔╝ █████╗  ███████║    ║
║   ██║     ██╔══██║██║╚██╗██║██║██╔══██║██╔═██╗ ██╔══╝  ██╔══██║    ║
║   ███████╗██║  ██║██║ ╚████║██║██║  ██║██║  ██╗███████╗██║  ██║    ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ║
║                                                                      ║
║              🌌 Intelligent Blockchain Protocol v3.0 🌌              ║
║                                                                      ║
║         Quantum-Resistant • AI-Powered • Self-Evolving              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""


class LaniakeAContext:
    """Context object for CLI commands"""
    
    def __init__(self):
        self.config = {}
        self.logger = None
        self.debug_mode = False
        self.dev_mode = False
        self.blockchain = None
        self.brain = None


pass_context = click.make_pass_decorator(LaniakeAContext, ensure=True)


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug mode with detailed logging')
@click.option('--dev', is_flag=True, help='Enable developer mode with hot reload and extra features')
@click.option('--config', type=click.Path(), help='Path to configuration file')
@click.version_option(version='3.0.0', prog_name='LaniakeA Protocol')
@pass_context
def cli(ctx: LaniakeAContext, debug: bool, dev: bool, config: Optional[str]):
    """
    🌌 LaniakeA Protocol - Intelligent Blockchain System
    
    A revolutionary blockchain protocol combining AI, quantum-resistant security,
    and cosmic consciousness for the next generation of decentralized applications.
    """
    # Print banner
    click.echo(click.style(LANIAKEA_BANNER, fg='cyan', bold=True))
    
    # Setup context
    ctx.debug_mode = debug
    ctx.dev_mode = dev
    
    # Setup logger
    log_level = logging.DEBUG if debug else logging.INFO
    ctx.logger = setup_logger('laniakea', log_level=log_level, dev_mode=dev)
    
    # Load configuration
    ctx.config = get_config()
    ctx.logger.debug("📁 Configuration loaded")
    
    if dev:
        ctx.logger.info("🔧 Developer mode enabled - Hot reload and extra features active")
    
    if debug:
        ctx.logger.debug("🐛 Debug mode enabled - Detailed logging active")


@cli.command()
@click.option('--node-id', default='laniakea-node-001', help='Unique identifier for this node')
@click.option('--host', default='0.0.0.0', help='Host address to bind to')
@click.option('--port', default=8000, type=int, help='Port number to listen on')
@click.option('--workers', default=4, type=int, help='Number of worker processes')
@click.option('--reload', is_flag=True, help='Enable auto-reload on code changes')
@pass_context
def start(ctx: LaniakeAContext, node_id: str, host: str, port: int, workers: int, reload: bool):
    """
    🚀 Start the LaniakeA Protocol node
    
    This command initializes and starts a full LaniakeA node with blockchain,
    AI intelligence, and network services.
    
    Examples:
        laniakea start --node-id my-node --port 8000
        laniakea start --dev --reload
    """
    ctx.logger.info("=" * 70)
    ctx.logger.info("🚀 Starting LaniakeA Protocol Node")
    ctx.logger.info("=" * 70)
    ctx.logger.info(f"📡 Node ID: {node_id}")
    ctx.logger.info(f"🌐 Host: {host}")
    ctx.logger.info(f"🔌 Port: {port}")
    ctx.logger.info(f"👷 Workers: {workers}")
    ctx.logger.info(f"🔄 Auto-reload: {'Enabled' if reload or ctx.dev_mode else 'Disabled'}")
    ctx.logger.info("=" * 70)
    
    try:
        # Initialize blockchain
        ctx.logger.info("⛓️  Initializing blockchain...")
        ctx.blockchain = HypercubeBlockchain(node_id=node_id, logger=ctx.logger)
        ctx.logger.info("✅ Blockchain initialized successfully")
        
        # Initialize AI brain
        if ctx.config.get('intelligence', {}).get('enabled', True):
            ctx.logger.info("🧠 Initializing Cosmic Brain AI...")
            ctx.brain = CosmicBrainAI(node_id=node_id, logger=ctx.logger)
            ctx.logger.info("✅ Cosmic Brain AI initialized successfully")
        
        # Create FastAPI app
        ctx.logger.info("🌐 Creating API server...")
        app = create_app(
            blockchain=ctx.blockchain,
            brain=ctx.brain,
            config=ctx.config,
            logger=ctx.logger,
            dev_mode=ctx.dev_mode
        )
        ctx.logger.info("✅ API server created successfully")
        
        # Start server
        ctx.logger.info("🎯 Starting server...")
        run_server(
            app=app,
            host=host,
            port=port,
            workers=workers,
            reload=reload or ctx.dev_mode,
            logger=ctx.logger
        )
        
    except KeyboardInterrupt:
        ctx.logger.info("\n🛑 Shutting down gracefully...")
    except Exception as e:
        ctx.logger.error(f"❌ Fatal error: {e}", exc_info=ctx.debug_mode)
        sys.exit(1)


@cli.command()
@click.option('--node-id', default='laniakea-node-001', help='Node identifier')
@click.option('--output', type=click.Path(), help='Output file for status report')
@pass_context
def status(ctx: LaniakeAContext, node_id: str, output: Optional[str]):
    """
    📊 Check the status of LaniakeA Protocol
    
    Display comprehensive system status including blockchain state,
    network health, AI intelligence metrics, and performance statistics.
    """
    ctx.logger.info("📊 Checking LaniakeA Protocol Status...")
    
    try:
        # Initialize blockchain
        blockchain = HypercubeBlockchain(node_id=node_id, logger=ctx.logger)
        
        # Get status
        status_data = blockchain.get_status()
        
        # Display status
        click.echo("\n" + "=" * 70)
        click.echo(click.style("📊 LaniakeA Protocol Status Report", fg='cyan', bold=True))
        click.echo("=" * 70)
        
        click.echo(f"\n🔗 Blockchain:")
        click.echo(f"  • Chain Length: {status_data.get('chain_length', 0)} blocks")
        click.echo(f"  • Latest Block: {status_data.get('latest_block_hash', 'N/A')[:16]}...")
        click.echo(f"  • Total Transactions: {status_data.get('total_transactions', 0)}")
        
        click.echo(f"\n🧠 Intelligence:")
        click.echo(f"  • AI Status: {status_data.get('ai_status', 'Unknown')}")
        click.echo(f"  • Evolution Level: {status_data.get('evolution_level', 0)}")
        click.echo(f"  • Learning Rate: {status_data.get('learning_rate', 0.0):.4f}")
        
        click.echo(f"\n🌐 Network:")
        click.echo(f"  • Connected Peers: {status_data.get('connected_peers', 0)}")
        click.echo(f"  • Network Status: {status_data.get('network_status', 'Unknown')}")
        
        click.echo(f"\n⚡ Performance:")
        click.echo(f"  • TPS (Transactions/sec): {status_data.get('tps', 0.0):.2f}")
        click.echo(f"  • CPU Usage: {status_data.get('cpu_usage', 0.0):.1f}%")
        click.echo(f"  • Memory Usage: {status_data.get('memory_usage', 0.0):.1f}%")
        
        click.echo("\n" + "=" * 70)
        
        # Save to file if requested
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(status_data, f, indent=2, default=str)
            ctx.logger.info(f"📄 Status report saved to: {output}")
        
        ctx.logger.info("✅ Status check completed")
        
    except Exception as e:
        ctx.logger.error(f"❌ Error checking status: {e}", exc_info=ctx.debug_mode)
        sys.exit(1)


@cli.command()
@click.option('--node-id', default='laniakea-node-001', help='Node identifier')
@click.option('--cycles', default=1, type=int, help='Number of evolution cycles to run')
@pass_context
def evolve(ctx: LaniakeAContext, node_id: str, cycles: int):
    """
    🧬 Trigger intelligent evolution
    
    Manually trigger the self-evolution process to improve system performance,
    learn new patterns, and adapt to changing conditions.
    """
    ctx.logger.info(f"🧬 Starting {cycles} evolution cycle(s)...")
    
    try:
        # Initialize AI brain
        brain = CosmicBrainAI(node_id=node_id, logger=ctx.logger)
        
        for i in range(cycles):
            ctx.logger.info(f"🔄 Evolution cycle {i+1}/{cycles}")
            
            # Run evolution
            result = asyncio.run(brain.evolve())
            
            ctx.logger.info(f"  ✅ Evolution completed:")
            ctx.logger.info(f"     • Performance improvement: {result.get('improvement', 0.0):.2%}")
            ctx.logger.info(f"     • New patterns learned: {result.get('new_patterns', 0)}")
            ctx.logger.info(f"     • Intelligence level: {result.get('intelligence_level', 0)}")
        
        ctx.logger.info("✅ All evolution cycles completed successfully")
        
    except Exception as e:
        ctx.logger.error(f"❌ Evolution error: {e}", exc_info=ctx.debug_mode)
        sys.exit(1)


@cli.command()
@click.option('--output', default='laniakea_config.yaml', help='Output configuration file')
@pass_context
def init(ctx: LaniakeAContext, output: str):
    """
    🔧 Initialize a new LaniakeA configuration
    
    Create a new configuration file with default settings that can be
    customized for your specific deployment needs.
    """
    ctx.logger.info("🔧 Initializing new LaniakeA configuration...")
    
    try:
        default_config = {
            'node': {
                'id': 'laniakea-node-001',
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 4
            },
            'blockchain': {
                'block_time': 20,
                'block_reward': 10.0,
                'difficulty': 4
            },
            'intelligence': {
                'enabled': True,
                'evolution_interval': 120,
                'learning_rate': 0.001
            },
            'security': {
                'encryption_enabled': True,
                'quantum_resistant': True,
                'rate_limit': 100
            },
            'network': {
                'p2p_enabled': True,
                'max_peers': 50,
                'discovery_enabled': True
            },
            'logging': {
                'level': 'INFO',
                'file': 'laniakea.log',
                'rotation': '100MB'
            }
        }
        
        save_config(default_config, output)
        ctx.logger.info(f"✅ Configuration file created: {output}")
        
        click.echo("\n📝 Next steps:")
        click.echo(f"  1. Edit {output} to customize your settings")
        click.echo(f"  2. Run: laniakea start --config {output}")
        
    except Exception as e:
        ctx.logger.error(f"❌ Initialization error: {e}", exc_info=ctx.debug_mode)
        sys.exit(1)


@cli.command()
@click.option('--format', type=click.Choice(['text', 'json', 'yaml']), default='text', help='Output format')
@pass_context
def info(ctx: LaniakeAContext, format: str):
    """
    ℹ️  Display LaniakeA Protocol information
    
    Show detailed information about the LaniakeA Protocol including
    version, features, and system capabilities.
    """
    info_data = {
        'name': 'LaniakeA Protocol',
        'version': '3.0.0',
        'description': 'Intelligent Blockchain Protocol with AI and Quantum Security',
        'features': [
            'Quantum-Resistant Cryptography',
            'Cosmic Brain AI',
            'Self-Evolution System',
            'Proof of Value Consensus',
            'Cross-Chain Compatibility',
            'Real-time WebSocket Updates',
            'Developer Mode with Hot Reload',
            'Comprehensive Logging & Monitoring'
        ],
        'author': 'LaniakeA Team',
        'license': 'MIT',
        'repository': 'https://github.com/QalamHipHop/laniakea-protocol'
    }
    
    if format == 'json':
        import json
        click.echo(json.dumps(info_data, indent=2))
    elif format == 'yaml':
        import yaml
        click.echo(yaml.dump(info_data, default_flow_style=False))
    else:
        click.echo("\n" + "=" * 70)
        click.echo(click.style(f"ℹ️  {info_data['name']} v{info_data['version']}", fg='cyan', bold=True))
        click.echo("=" * 70)
        click.echo(f"\n📝 {info_data['description']}\n")
        click.echo("✨ Features:")
        for feature in info_data['features']:
            click.echo(f"  • {feature}")
        click.echo(f"\n👤 Author: {info_data['author']}")
        click.echo(f"📜 License: {info_data['license']}")
        click.echo(f"🔗 Repository: {info_data['repository']}")
        click.echo("=" * 70 + "\n")


@cli.group()
def dev():
    """
    🔧 Developer tools and utilities
    
    Advanced tools for developers including code generation,
    testing utilities, and debugging helpers.
    """
    pass


@dev.command()
@click.option('--watch', is_flag=True, help='Watch for changes and auto-reload')
@pass_context
def logs(ctx: LaniakeAContext, watch: bool):
    """
    📋 View LaniakeA logs
    
    Display and optionally watch the LaniakeA log files in real-time.
    """
    ctx.logger.info("📋 Displaying logs...")
    
    log_file = ctx.config.get('logging', {}).get('file', 'laniakea.log')
    
    if not os.path.exists(log_file):
        ctx.logger.warning(f"⚠️  Log file not found: {log_file}")
        return
    
    try:
        if watch:
            # Tail -f equivalent
            import subprocess
            subprocess.run(['tail', '-f', log_file])
        else:
            # Display last 50 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    click.echo(line.rstrip())
    except Exception as e:
        ctx.logger.error(f"❌ Error reading logs: {e}", exc_info=ctx.debug_mode)


@dev.command()
@pass_context
def test(ctx: LaniakeAContext):
    """
    🧪 Run test suite
    
    Execute the full test suite including unit tests, integration tests,
    and performance benchmarks.
    """
    ctx.logger.info("🧪 Running test suite...")
    
    try:
        import subprocess
        result = subprocess.run(['pytest', 'tests/', '-v', '--cov=laniakea'], 
                              capture_output=True, text=True)
        
        click.echo(result.stdout)
        if result.returncode != 0:
            click.echo(result.stderr)
            sys.exit(result.returncode)
        
        ctx.logger.info("✅ All tests passed")
        
    except Exception as e:
        ctx.logger.error(f"❌ Test error: {e}", exc_info=ctx.debug_mode)
        sys.exit(1)


if __name__ == '__main__':
    cli()
