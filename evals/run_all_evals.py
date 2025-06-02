#!/usr/bin/env python3
"""
Master Evaluation Runner
Runs all evaluation suites and provides comprehensive reporting.
"""

import asyncio
import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all evaluation modules
from evals.session_evals import run_session_evals
from evals.agent_evals import run_agent_evals
from evals.performance_evals import run_performance_evals
from evals.callback_evals import run_callback_evaluations
from evals.preference_evals import run_preference_evaluations

class EvaluationReport:
    """Generates comprehensive evaluation reports."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.results = {}
        
    def start_evaluation(self):
        """Mark the start of evaluation."""
        self.start_time = datetime.now()
        print(f"🚀 Starting Comprehensive Evaluation Suite")
        print(f"   Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def end_evaluation(self):
        """Mark the end of evaluation."""
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        print("\n" + "=" * 80)
        print(f"🏁 Evaluation Suite Completed")
        print(f"   Completed at: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Duration: {duration}")
    
    def add_suite_results(self, suite_name: str, results: List[Dict[str, Any]], duration: float):
        """Add results from an evaluation suite."""
        self.results[suite_name] = {
            "results": results,
            "duration": duration,
            "total_tests": len(results),
            "passed_tests": sum(1 for r in results if r.get("passed", False)),
            "failed_tests": sum(1 for r in results if not r.get("passed", False))
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary of all evaluations."""
        summary = {
            "evaluation_info": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_duration": str(self.end_time - self.start_time) if self.start_time and self.end_time else None
            },
            "suites": {},
            "overall": {
                "total_suites": len(self.results),
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
                "success_rate": 0.0
            }
        }
        
        # Process each suite
        for suite_name, suite_data in self.results.items():
            summary["suites"][suite_name] = {
                "duration": suite_data["duration"],
                "total_tests": suite_data["total_tests"],
                "passed_tests": suite_data["passed_tests"],
                "failed_tests": suite_data["failed_tests"],
                "success_rate": suite_data["passed_tests"] / suite_data["total_tests"] if suite_data["total_tests"] > 0 else 0.0
            }
            
            # Add to overall totals
            summary["overall"]["total_tests"] += suite_data["total_tests"]
            summary["overall"]["total_passed"] += suite_data["passed_tests"]
            summary["overall"]["total_failed"] += suite_data["failed_tests"]
        
        # Calculate overall success rate
        if summary["overall"]["total_tests"] > 0:
            summary["overall"]["success_rate"] = summary["overall"]["total_passed"] / summary["overall"]["total_tests"]
        
        return summary
    
    def print_detailed_summary(self):
        """Print detailed summary to console."""
        summary = self.generate_summary()
        
        print("\n" + "🎯" * 30)
        print("📊 COMPREHENSIVE EVALUATION SUMMARY")
        print("🎯" * 30)
        
        # Overall stats
        overall = summary["overall"]
        print(f"\n📈 Overall Results:")
        print(f"   Total Suites: {overall['total_suites']}")
        print(f"   Total Tests: {overall['total_tests']}")
        print(f"   Passed: {overall['total_passed']} ✅")
        print(f"   Failed: {overall['total_failed']} ❌")
        print(f"   Success Rate: {overall['success_rate']:.1%}")
        
        # Suite breakdown
        print(f"\n📋 Suite Breakdown:")
        for suite_name, suite_data in summary["suites"].items():
            status_icon = "✅" if suite_data["success_rate"] == 1.0 else "⚠️" if suite_data["success_rate"] >= 0.8 else "❌"
            print(f"   {status_icon} {suite_name}:")
            print(f"      Tests: {suite_data['passed_tests']}/{suite_data['total_tests']} ({suite_data['success_rate']:.1%})")
            print(f"      Duration: {suite_data['duration']:.2f}s")
        
        # Performance metrics
        if "performance_evals" in summary["suites"]:
            print(f"\n⚡ Performance Highlights:")
            perf_results = self.results["performance_evals"]["results"]
            for result in perf_results:
                if result.get("metrics"):
                    metrics = result["metrics"]
                    test_name = result.get("test_name", "unknown")
                    print(f"   {test_name}:")
                    for key, value in metrics.items():
                        if isinstance(value, float) and "time" in key:
                            print(f"      {key}: {value:.3f}s")
        
        # Agent quality metrics
        if "agent_evals" in summary["suites"]:
            print(f"\n🤖 Agent Quality Highlights:")
            agent_results = self.results["agent_evals"]["results"]
            quality_scores = []
            for result in agent_results:
                if result.get("metrics") and "response_quality_score" in result["metrics"]:
                    quality_scores.append(result["metrics"]["response_quality_score"])
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"   Average Quality Score: {avg_quality:.2f}/1.0")
                print(f"   Best Quality Score: {max(quality_scores):.2f}/1.0")
        
        # Callback system metrics
        if "callback_evals" in summary["suites"]:
            print(f"\n🔗 Callback System Highlights:")
            callback_results = self.results["callback_evals"]["results"]
            for result in callback_results:
                if result.get("metrics"):
                    metrics = result["metrics"]
                    test_name = result.get("test_name", "unknown")
                    if "integration" in test_name:
                        print(f"   {test_name}: {result.get('passed', False)} ✅" if result.get('passed') else f"   {test_name}: ❌")
                    elif "duration" in str(metrics):
                        for key, value in metrics.items():
                            if isinstance(value, float) and "duration" in key:
                                print(f"   {test_name} {key}: {value:.3f}s")
        
        # Preference system metrics
        if "preference_evals" in summary["suites"]:
            print(f"\n🎯 Preference System Highlights:")
            pref_results = self.results["preference_evals"]["results"]
            
            # Extract preference detection metrics
            for result in pref_results:
                if result.get("test_name") == "preference_detection" and result.get("metrics"):
                    detection_rate = result["metrics"].get("success_rate", 0)
                    print(f"   Preference Detection Rate: {detection_rate:.1%}")
                    
                if result.get("test_name") == "preference_tools" and result.get("metrics"):
                    tool_success = result["metrics"].get("tool_operations_passed", 0)
                    tool_total = result["metrics"].get("total_tool_operations", 1)
                    print(f"   Tool Operations Success: {tool_success}/{tool_total}")
        
        # Final verdict
        print(f"\n🎯 Final Verdict:")
        if overall["success_rate"] >= 0.95:
            print("   🏆 EXCELLENT - System performing exceptionally well!")
        elif overall["success_rate"] >= 0.85:
            print("   ✅ GOOD - System performing well with minor issues")
        elif overall["success_rate"] >= 0.70:
            print("   ⚠️  NEEDS ATTENTION - Several issues need addressing")
        else:
            print("   ❌ CRITICAL - Major issues require immediate attention")
        
    def save_detailed_report(self, filename: str = None):
        """Save detailed report to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eval_report_{timestamp}.json"
        
        report_data = {
            "summary": self.generate_summary(),
            "detailed_results": self.results
        }
        
        report_path = Path("evals") / filename
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_path}")
        return report_path

async def run_evaluation_suite(suite_name: str, suite_function, report: EvaluationReport):
    """Run a single evaluation suite and track results."""
    print(f"\n🔄 Running {suite_name}...")
    start_time = time.time()
    
    try:
        results = await suite_function()
        duration = time.time() - start_time
        
        # Add results to report
        report.add_suite_results(suite_name, results, duration)
        
        # Print suite summary
        passed = sum(1 for r in results if r.get("passed", False))
        total = len(results)
        print(f"✅ {suite_name} completed: {passed}/{total} tests passed ({duration:.2f}s)")
        
        return results
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ {suite_name} failed: {str(e)} ({duration:.2f}s)")
        
        # Add failed suite to report
        report.add_suite_results(suite_name, [{"test_name": suite_name, "passed": False, "errors": [str(e)]}], duration)
        return []

async def main():
    """Run all evaluation suites."""
    report = EvaluationReport()
    report.start_evaluation()
    
    # Define evaluation suites
    suites = [
        ("session_evals", run_session_evals),
        ("agent_evals", run_agent_evals),
        ("callback_evals", run_callback_evaluations),
        ("preference_evals", run_preference_evaluations),
        ("performance_evals", run_performance_evals)
    ]
    
    # Run all suites
    for suite_name, suite_function in suites:
        await run_evaluation_suite(suite_name, suite_function, report)
        
        # Brief pause between suites
        await asyncio.sleep(1)
    
    # Generate final report
    report.end_evaluation()
    report.print_detailed_summary()
    
    # Save detailed report
    try:
        report_path = report.save_detailed_report()
        return report_path
    except Exception as e:
        print(f"⚠️  Failed to save report: {e}")
        return None

if __name__ == "__main__":
    try:
        report_path = asyncio.run(main())
        print(f"\n🎉 Evaluation suite completed successfully!")
        if report_path:
            print(f"📄 Report available at: {report_path}")
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
    except Exception as e:
        print(f"\n�� Evaluation failed: {e}")
        import traceback
        traceback.print_exc() 