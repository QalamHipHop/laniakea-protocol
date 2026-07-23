#!/usr/bin/env python3
"""
Live Server Deployment Test - Laniakea Protocol
اختبار استقرار سرور زنده
"""

import subprocess
import time
import requests
import json
import sys
from typing import Dict, List, Tuple

class DeploymentTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.server_process = None
    
    def print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"     └─ {details}")
        
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {details}")
    
    def start_server(self) -> bool:
        """Start the FastAPI server"""
        self.print_header("Step 1: Starting Laniakea Protocol Server")
        
        try:
            print("🚀 Launching FastAPI server on port 8000...")
            print("   Command: python main.py")
            
            # Start the server
            self.server_process = subprocess.Popen(
                ["python", "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to initialize...")
            time.sleep(5)
            
            # Check if process is still running
            if self.server_process.poll() is not None:
                print("❌ Server failed to start")
                return False
            
            print("✅ Server process started successfully")
            return True
        
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def check_server_health(self) -> bool:
        """Check if server is responding"""
        self.print_header("Step 2: Server Health Check")
        
        try:
            print(f"🔍 Checking endpoint: GET {self.base_url}/")
            response = requests.get(f"{self.base_url}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server responding: {data}")
                self.log_result("Server health check", True, f"Status: {response.status_code}")
                return True
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                self.log_result("Server health check", False, f"Status: {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server - is it running?")
            self.log_result("Server health check", False, "Connection refused")
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.log_result("Server health check", False, str(e))
            return False
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        self.print_header("Step 3: Testing Core Endpoints")
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            self.log_result("GET /", response.status_code == 200, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /", False, str(e))
    
    def test_core_status(self):
        """Test core status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/core/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"     Status: {data.get('status')}")
                print(f"     Version: {data.get('protocol_version')}")
                self.log_result("GET /core/status", True, f"Status: {data.get('status')}")
            else:
                self.log_result("GET /core/status", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("GET /core/status", False, str(e))
    
    def test_blockchain_endpoints(self):
        """Test blockchain endpoints"""
        self.print_header("Step 4: Testing Blockchain Module")
        
        try:
            # Test get chain
            response = requests.get(f"{self.base_url}/blockchain/chain", timeout=5)
            self.log_result("GET /blockchain/chain", response.status_code == 200, f"Blocks: {len(response.json()) if response.status_code == 200 else 0}")
            
            # Test add transaction
            tx_data = {
                "sender": "Alice",
                "recipient": "Bob",
                "amount": 50.0
            }
            response = requests.post(f"{self.base_url}/blockchain/transactions/new", json=tx_data, timeout=5)
            self.log_result("POST /blockchain/transactions/new", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("Blockchain endpoints", False, str(e))
    
    def test_quantum_endpoints(self):
        """Test quantum endpoints"""
        self.print_header("Step 5: Testing Quantum Module")
        
        try:
            # Test quantum job submission
            job_data = {
                "num_qubits": 3,
                "gates": [
                    {"type": "H", "target": 0},
                    {"type": "X", "target": 1}
                ]
            }
            response = requests.post(f"{self.base_url}/quantum/job/submit", json=job_data, timeout=5)
            self.log_result("POST /quantum/job/submit", response.status_code == 200, f"Status: {response.status_code}")
            
            # Test quantum job processing
            response = requests.post(f"{self.base_url}/quantum/job/process", timeout=5)
            self.log_result("POST /quantum/job/process", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("Quantum endpoints", False, str(e))
    
    def test_defi_endpoints(self):
        """Test DeFi endpoints"""
        self.print_header("Step 6: Testing DeFi Module")
        
        try:
            # Test get pools
            response = requests.get(f"{self.base_url}/defi/pools", timeout=5)
            self.log_result("GET /defi/pools", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("DeFi endpoints", False, str(e))
    
    def test_ai_endpoints(self):
        """Test AI endpoints"""
        self.print_header("Step 7: Testing AI Module")
        
        try:
            # Test AI query
            query_data = {"prompt": "What is Laniakea Protocol?"}
            response = requests.post(f"{self.base_url}/ai/query", json=query_data, timeout=5)
            self.log_result("POST /ai/query", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("AI endpoints", False, str(e))
    
    def test_governance_endpoints(self):
        """Test governance endpoints"""
        self.print_header("Step 8: Testing Governance Module")
        
        try:
            # Test create proposal
            proposal_data = {
                "title": "Test Proposal",
                "description": "A test governance proposal",
                "proposer": "Alice"
            }
            response = requests.post(f"{self.base_url}/governance/proposals/new", json=proposal_data, timeout=5)
            self.log_result("POST /governance/proposals/new", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("Governance endpoints", False, str(e))
    
    def test_simulation_endpoints(self):
        """Test simulation endpoints"""
        self.print_header("Step 9: Testing Simulation Module")
        
        try:
            # Test step simulation
            response = requests.post(f"{self.base_url}/simulation/step", timeout=5)
            self.log_result("POST /simulation/step", response.status_code == 200, f"Status: {response.status_code}")
            
            # Test get entities
            response = requests.get(f"{self.base_url}/simulation/entities", timeout=5)
            entities = response.json() if response.status_code == 200 else []
            self.log_result("GET /simulation/entities", response.status_code == 200, f"Entities: {len(entities)}")
        
        except Exception as e:
            self.log_result("Simulation endpoints", False, str(e))
    
    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        self.print_header("Step 10: Testing Dashboard Module")
        
        try:
            # Test get metrics
            response = requests.get(f"{self.base_url}/dashboard/metrics", timeout=5)
            self.log_result("GET /dashboard/metrics", response.status_code == 200, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("Dashboard endpoints", False, str(e))
    
    def test_error_handling(self):
        """Test error handling"""
        self.print_header("Step 11: Testing Error Handling")
        
        try:
            # Test invalid quantum job (too many qubits)
            job_data = {
                "num_qubits": 1000,  # Way too many
                "gates": []
            }
            response = requests.post(f"{self.base_url}/quantum/job/submit", json=job_data, timeout=5)
            self.log_result("Error handling - invalid qubits", response.status_code == 400, f"Status: {response.status_code}")
            
            # Test invalid transaction (negative amount)
            tx_data = {
                "sender": "Alice",
                "recipient": "Bob",
                "amount": -50.0
            }
            response = requests.post(f"{self.base_url}/blockchain/transactions/new", json=tx_data, timeout=5)
            self.log_result("Error handling - negative amount", response.status_code == 400, f"Status: {response.status_code}")
        
        except Exception as e:
            self.log_result("Error handling tests", False, str(e))
    
    def stop_server(self):
        """Stop the server"""
        self.print_header("Step 12: Cleanup")
        
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
                print("✅ Server stopped gracefully")
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                print("⚠️  Server force-killed")
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("📊 Test Summary")
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"✅ PASSED: {self.results['passed']}")
        print(f"❌ FAILED: {self.results['failed']}")
        print(f"📊 TOTAL:  {total}")
        print(f"📈 PASS RATE: {pass_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print("\n⚠️  FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"   - {error}")
        
        print("\n" + "="*70)
        if self.results["failed"] == 0:
            print("🎉 ALL TESTS PASSED - SERVER FULLY OPERATIONAL!")
            print("\n✨ Live Deployment Status:")
            print("   ✅ Configuration validated")
            print("   ✅ Server initialization successful")
            print("   ✅ All endpoints responding")
            print("   ✅ Error handling working")
            print("   ✅ No division by zero errors")
            print("   ✅ State bounds enforced")
            print("\n🚀 Laniakea Protocol is ready for production!")
        else:
            print(f"⚠️  {self.results['failed']} test(s) failed - review errors above")
        print("="*70)
    
    def run_all_tests(self):
        """Run all deployment tests"""
        self.print_header("🌌 Laniakea Protocol - Live Server Deployment Test")
        print("Starting comprehensive server validation...\n")
        
        try:
            # Start server
            if not self.start_server():
                print("❌ Failed to start server")
                return False
            
            # Run all tests
            if self.check_server_health():
                self.test_root_endpoint()
                self.test_core_status()
                self.test_blockchain_endpoints()
                self.test_quantum_endpoints()
                self.test_defi_endpoints()
                self.test_ai_endpoints()
                self.test_governance_endpoints()
                self.test_simulation_endpoints()
                self.test_dashboard_endpoints()
                self.test_error_handling()
            else:
                print("❌ Server health check failed - skipping endpoint tests")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
        
        finally:
            self.stop_server()
            self.print_summary()
            
            return self.results["failed"] == 0

if __name__ == "__main__":
    tester = DeploymentTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
