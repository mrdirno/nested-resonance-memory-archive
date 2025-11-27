#!/usr/bin/env python3
"""
Enterprise FPGA Timing Analysis Tool
Production-ready timing analysis and optimization for $150K/month projects

Description: Advanced timing analysis tool with automated optimization
             suggestions and enterprise-grade reporting
Author: FPGA Development Team  
Date: 2025-07-23
Version: 1.0.0
"""

import os
import sys
import re
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('timing_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TimingPath:
    """Represents a timing path with all relevant information"""
    start_point: str
    end_point: str
    slack: float
    requirement: float
    delay: float
    logic_delay: float
    route_delay: float
    path_type: str  # setup, hold, recovery, removal
    clock_domain: str
    
@dataclass
class ClockDomain:
    """Represents a clock domain with its characteristics"""
    name: str
    frequency: float
    period: float
    source: str
    fanout: int
    skew: float
    jitter: float

@dataclass
class TimingViolation:
    """Represents a timing violation with severity and recommendations"""
    path: TimingPath
    severity: str  # critical, high, medium, low
    violation_type: str
    recommended_actions: List[str]
    estimated_improvement: float

class EnterpriseTimingAnalyzer:
    """Enterprise-grade timing analysis tool for FPGA designs"""
    
    def __init__(self, project_root: str, config_file: str = None):
        self.project_root = Path(project_root)
        self.config_file = config_file
        self.timing_paths: List[TimingPath] = []
        self.clock_domains: List[ClockDomain] = []
        self.violations: List[TimingViolation] = []
        self.config = self._load_config()
        
        # Enterprise timing requirements
        self.CRITICAL_SLACK_THRESHOLD = -0.5  # ns
        self.WARNING_SLACK_THRESHOLD = 0.1   # ns
        self.TARGET_MARGIN = 0.5              # ns
        self.MAX_CLOCK_SKEW = 0.2            # ns
        self.MAX_JITTER = 0.1                # ns
        
    def _load_config(self) -> Dict:
        """Load project configuration from YAML file"""
        try:
            config_path = self.project_root / "project_config" / "project_settings.yml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file not found: {config_path}")
                return self._default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'design': {
                'clock_frequency': 250,
                'timing_margin': 0.5,
                'target_utilization': 80
            },
            'tools': {
                'synthesis': 'vivado'
            }
        }
    
    def parse_vivado_timing_report(self, report_path: str) -> None:
        """Parse Vivado timing report and extract timing paths"""
        logger.info(f"Parsing Vivado timing report: {report_path}")
        
        try:
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Parse timing paths using regex patterns
            path_pattern = r'Path\s+(\d+):.*?Slack.*?(-?\d+\.?\d*)\s*ns.*?(?=Path\s+\d+:|$)'
            
            for match in re.finditer(path_pattern, content, re.DOTALL):
                path_text = match.group(0)
                slack = float(match.group(2))
                
                # Extract more details from path text
                start_point = self._extract_start_point(path_text)
                end_point = self._extract_end_point(path_text)
                requirement = self._extract_requirement(path_text)
                delay = self._extract_delay(path_text)
                logic_delay = self._extract_logic_delay(path_text)
                route_delay = delay - logic_delay if delay and logic_delay else 0.0
                path_type = self._extract_path_type(path_text)
                clock_domain = self._extract_clock_domain(path_text)
                
                timing_path = TimingPath(
                    start_point=start_point,
                    end_point=end_point,
                    slack=slack,
                    requirement=requirement,
                    delay=delay,
                    logic_delay=logic_delay,
                    route_delay=route_delay,
                    path_type=path_type,
                    clock_domain=clock_domain
                )
                
                self.timing_paths.append(timing_path)
                
        except FileNotFoundError:
            logger.error(f"Timing report file not found: {report_path}")
        except Exception as e:
            logger.error(f"Error parsing timing report: {e}")
    
    def _extract_start_point(self, path_text: str) -> str:
        """Extract start point from timing path text"""
        match = re.search(r'Source:\s*(\S+)', path_text)
        return match.group(1) if match else "unknown"
    
    def _extract_end_point(self, path_text: str) -> str:
        """Extract end point from timing path text"""
        match = re.search(r'Destination:\s*(\S+)', path_text)
        return match.group(1) if match else "unknown"
    
    def _extract_requirement(self, path_text: str) -> float:
        """Extract timing requirement from path text"""
        match = re.search(r'Requirement:\s*(-?\d+\.?\d*)', path_text)
        return float(match.group(1)) if match else 0.0
    
    def _extract_delay(self, path_text: str) -> float:
        """Extract total delay from path text"""
        match = re.search(r'Data Path Delay:\s*(-?\d+\.?\d*)', path_text)
        return float(match.group(1)) if match else 0.0
    
    def _extract_logic_delay(self, path_text: str) -> float:
        """Extract logic delay from path text"""
        match = re.search(r'Logic Delay:\s*(-?\d+\.?\d*)', path_text)
        return float(match.group(1)) if match else 0.0
    
    def _extract_path_type(self, path_text: str) -> str:
        """Extract path type (setup, hold, etc.)"""
        if 'Setup' in path_text:
            return 'setup'
        elif 'Hold' in path_text:
            return 'hold'
        elif 'Recovery' in path_text:
            return 'recovery'
        elif 'Removal' in path_text:
            return 'removal'
        else:
            return 'unknown'
    
    def _extract_clock_domain(self, path_text: str) -> str:
        """Extract clock domain from path text"""
        match = re.search(r'Clock:\s*(\S+)', path_text)
        return match.group(1) if match else "unknown"
    
    def analyze_clock_domains(self, report_path: str) -> None:
        """Analyze clock domains from clock utilization report"""
        logger.info("Analyzing clock domains...")
        
        try:
            with open(report_path, 'r') as f:
                content = f.read()
            
            # Parse clock domain information
            clock_pattern = r'(\w+)\s+(\d+\.?\d*)\s+MHz.*?(\d+)\s+fanout'
            
            for match in re.finditer(clock_pattern, content):
                name = match.group(1)
                frequency = float(match.group(2))
                fanout = int(match.group(3))
                
                clock_domain = ClockDomain(
                    name=name,
                    frequency=frequency,
                    period=1000.0 / frequency,  # Convert to ns
                    source="PLL",  # Default assumption
                    fanout=fanout,
                    skew=0.0,  # Would need dedicated skew report
                    jitter=0.05  # Typical assumption
                )
                
                self.clock_domains.append(clock_domain)
                
        except FileNotFoundError:
            logger.warning(f"Clock utilization report not found: {report_path}")
        except Exception as e:
            logger.error(f"Error analyzing clock domains: {e}")
    
    def identify_violations(self) -> None:
        """Identify timing violations and categorize by severity"""
        logger.info("Identifying timing violations...")
        
        for path in self.timing_paths:
            if path.slack < self.CRITICAL_SLACK_THRESHOLD:
                severity = "critical"
            elif path.slack < 0:
                severity = "high"
            elif path.slack < self.WARNING_SLACK_THRESHOLD:
                severity = "medium"
            else:
                continue  # No violation
            
            # Generate recommendations based on violation characteristics
            recommendations = self._generate_recommendations(path)
            
            violation = TimingViolation(
                path=path,
                severity=severity,
                violation_type=path.path_type,
                recommended_actions=recommendations,
                estimated_improvement=self._estimate_improvement(path, recommendations)
            )
            
            self.violations.append(violation)
    
    def _generate_recommendations(self, path: TimingPath) -> List[str]:
        """Generate optimization recommendations for a timing path"""
        recommendations = []
        
        # Analyze delay breakdown
        if path.route_delay > path.logic_delay * 2:
            recommendations.append("Consider floorplanning to reduce routing delay")
            recommendations.append("Add pipeline registers to break long routing paths")
            
        if path.logic_delay > path.route_delay * 2:
            recommendations.append("Optimize logic depth - consider parallel processing")
            recommendations.append("Use faster speed grade components if available")
            
        # Path-specific recommendations
        if path.path_type == "setup":
            recommendations.append("Increase clock period or add pipeline stages")
            recommendations.append("Use timing-driven placement and routing")
            
        elif path.path_type == "hold":
            recommendations.append("Add delay elements or buffer chains")
            recommendations.append("Adjust clock skew optimization")
        
        # Clock domain specific
        clock_freq = self.config.get('design', {}).get('clock_frequency', 250)
        if path.requirement < (1000.0 / clock_freq) * 0.9:  # Less than 90% of period
            recommendations.append("Consider clock domain crossing optimization")
            
        return recommendations
    
    def _estimate_improvement(self, path: TimingPath, recommendations: List[str]) -> float:
        """Estimate potential timing improvement from recommendations"""
        improvement = 0.0
        
        for rec in recommendations:
            if "pipeline" in rec.lower():
                improvement += 2.0  # Typical pipeline improvement
            elif "floorplan" in rec.lower():
                improvement += 1.0  # Routing improvement
            elif "logic" in rec.lower():
                improvement += 0.5  # Logic optimization
            elif "buffer" in rec.lower():
                improvement += 0.2  # Buffer improvement
                
        return min(improvement, abs(path.slack) + self.TARGET_MARGIN)
    
    def generate_optimization_tcl(self, output_path: str) -> None:
        """Generate TCL script with optimization directives"""
        logger.info(f"Generating optimization TCL script: {output_path}")
        
        tcl_content = [
            "# Enterprise FPGA Timing Optimization Script",
            f"# Generated: {datetime.now()}",
            "# Production-ready timing optimization for $150K/month projects",
            "",
            "# Set timing-driven synthesis options",
            "set_param synth.elaboration.rodinMoreOptions {rt::set_parameter maxStepsInFlatten 200000}",
            "set_param synth.synthesis.reconstruct_LUT6_threshold 10",
            "",
            "# Optimization directives based on timing analysis",
        ]
        
        # Add specific optimizations based on violations
        critical_violations = [v for v in self.violations if v.severity == "critical"]
        
        if critical_violations:
            tcl_content.extend([
                "",
                "# Critical timing violations found - applying aggressive optimization",
                "set_property strategy Performance_ExplorePostRoutePhysOpt [get_runs impl_1]",
                "set_property STEPS.OPT_DESIGN.ARGS.DIRECTIVE ExploreWithRemap [get_runs impl_1]",
                "set_property STEPS.PLACE_DESIGN.ARGS.DIRECTIVE ExtraTimingOpt [get_runs impl_1]",
                "set_property STEPS.PHYS_OPT_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]",
                "set_property STEPS.ROUTE_DESIGN.ARGS.DIRECTIVE AggressiveExplore [get_runs impl_1]",
            ])
        
        # Add clock-specific optimizations
        for clock in self.clock_domains:
            if clock.frequency > 300:  # High-frequency clocks
                tcl_content.extend([
                    f"",
                    f"# High-frequency clock optimization for {clock.name}",
                    f"set_property CLOCK_BUFFER_TYPE BUFGCE [get_nets {clock.name}]",
                ])
        
        # Add floorplanning suggestions for critical paths
        for violation in critical_violations[:5]:  # Top 5 critical paths
            tcl_content.extend([
                f"",
                f"# Floorplanning suggestion for critical path",
                f"# From: {violation.path.start_point} To: {violation.path.end_point}",
                f"# Consider creating pblock or using LOC constraints",
            ])
        
        # Write TCL file
        try:
            with open(output_path, 'w') as f:
                f.write('\n'.join(tcl_content))
            logger.info("Optimization TCL script generated successfully")
        except Exception as e:
            logger.error(f"Error writing TCL script: {e}")
    
    def generate_html_report(self, output_path: str) -> None:
        """Generate comprehensive HTML timing report"""
        logger.info(f"Generating HTML timing report: {output_path}")
        
        # Calculate summary statistics
        total_paths = len(self.timing_paths)
        failing_paths = len([p for p in self.timing_paths if p.slack < 0])
        critical_violations = len([v for v in self.violations if v.severity == "critical"])
        worst_slack = min([p.slack for p in self.timing_paths]) if self.timing_paths else 0.0
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Enterprise FPGA Timing Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .critical {{ border-left-color: #dc3545; }}
        .warning {{ border-left-color: #ffc107; }}
        .success {{ border-left-color: #28a745; }}
        .violations {{ margin: 30px 0; }}
        .violation {{ background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 10px 0; }}
        .violation.critical {{ background-color: #f8d7da; border-color: #f5c6cb; }}
        .recommendations {{ background-color: #d1ecf1; border: 1px solid #bee5eb; border-radius: 5px; padding: 15px; margin: 10px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        .path-details {{ font-family: monospace; font-size: 12px; }}
        .clock-domain {{ background-color: #e9ecef; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Enterprise FPGA Timing Analysis Report</h1>
            <p><strong>Project:</strong> {self.config.get('project', {}).get('name', 'Enterprise FPGA Project')}</p>
            <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Project Value:</strong> $150K/month</p>
        </div>
        
        <div class="summary">
            <div class="metric {'critical' if failing_paths > 0 else 'success'}">
                <h3>{total_paths}</h3>
                <p>Total Timing Paths</p>
            </div>
            <div class="metric {'critical' if failing_paths > 0 else 'success'}">
                <h3>{failing_paths}</h3>
                <p>Failing Paths</p>
            </div>
            <div class="metric {'critical' if critical_violations > 0 else 'success'}">
                <h3>{critical_violations}</h3>
                <p>Critical Violations</p>
            </div>
            <div class="metric {'critical' if worst_slack < 0 else 'success'}">
                <h3>{worst_slack:.3f} ns</h3>
                <p>Worst Slack</p>
            </div>
        </div>
        
        <h2>Clock Domains Analysis</h2>
        <div class="clock-domains">
"""
        
        for clock in self.clock_domains:
            html_content += f"""
            <div class="clock-domain">
                <h4>{clock.name}</h4>
                <p><strong>Frequency:</strong> {clock.frequency:.1f} MHz | 
                   <strong>Period:</strong> {clock.period:.3f} ns | 
                   <strong>Fanout:</strong> {clock.fanout}</p>
            </div>
"""
        
        html_content += """
        </div>
        
        <h2>Critical Timing Violations</h2>
        <div class="violations">
"""
        
        # Show top 10 critical violations
        critical_violations_list = [v for v in self.violations if v.severity in ["critical", "high"]][:10]
        
        for i, violation in enumerate(critical_violations_list, 1):
            html_content += f"""
            <div class="violation {violation.severity}">
                <h4>Violation #{i} - {violation.severity.upper()}</h4>
                <div class="path-details">
                    <p><strong>Path:</strong> {violation.path.start_point} → {violation.path.end_point}</p>
                    <p><strong>Slack:</strong> {violation.path.slack:.3f} ns | 
                       <strong>Requirement:</strong> {violation.path.requirement:.3f} ns | 
                       <strong>Type:</strong> {violation.path.path_type}</p>
                    <p><strong>Delay Breakdown:</strong> Logic: {violation.path.logic_delay:.3f} ns, 
                       Route: {violation.path.route_delay:.3f} ns</p>
                </div>
                <div class="recommendations">
                    <h5>Recommended Actions:</h5>
                    <ul>
"""
            
            for rec in violation.recommended_actions:
                html_content += f"<li>{rec}</li>"
            
            html_content += f"""
                    </ul>
                    <p><strong>Estimated Improvement:</strong> {violation.estimated_improvement:.3f} ns</p>
                </div>
            </div>
"""
        
        html_content += """
        </div>
        
        <h2>Detailed Timing Paths</h2>
        <table>
            <tr>
                <th>Start Point</th>
                <th>End Point</th>
                <th>Slack (ns)</th>
                <th>Requirement (ns)</th>
                <th>Logic Delay (ns)</th>
                <th>Route Delay (ns)</th>
                <th>Type</th>
                <th>Clock Domain</th>
            </tr>
"""
        
        # Show worst 20 paths
        worst_paths = sorted(self.timing_paths, key=lambda p: p.slack)[:20]
        
        for path in worst_paths:
            row_class = "critical" if path.slack < 0 else "warning" if path.slack < self.WARNING_SLACK_THRESHOLD else ""
            html_content += f"""
            <tr class="{row_class}">
                <td>{path.start_point}</td>
                <td>{path.end_point}</td>
                <td>{path.slack:.3f}</td>
                <td>{path.requirement:.3f}</td>
                <td>{path.logic_delay:.3f}</td>
                <td>{path.route_delay:.3f}</td>
                <td>{path.path_type}</td>
                <td>{path.clock_domain}</td>
            </tr>
"""
        
        html_content += """
        </table>
        
        <div style="margin-top: 40px; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
            <h3>Enterprise Quality Summary</h3>
            <p>This timing analysis report provides comprehensive insights for production-ready FPGA designs 
               targeting $150K/month project requirements. All critical violations must be resolved before 
               deployment to ensure reliable operation in enterprise environments.</p>
        </div>
    </div>
</body>
</html>
"""
        
        try:
            with open(output_path, 'w') as f:
                f.write(html_content)
            logger.info("HTML timing report generated successfully")
        except Exception as e:
            logger.error(f"Error writing HTML report: {e}")
    
    def run_analysis(self, timing_report_path: str, clock_report_path: str = None) -> None:
        """Run complete timing analysis workflow"""
        logger.info("Starting enterprise timing analysis...")
        
        # Parse timing reports
        if timing_report_path:
            self.parse_vivado_timing_report(timing_report_path)
        
        if clock_report_path:
            self.analyze_clock_domains(clock_report_path)
        
        # Analyze violations
        self.identify_violations()
        
        # Generate output files
        output_dir = self.project_root / "build" / "reports" / "timing"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate optimization script
        tcl_path = output_dir / f"timing_optimization_{timestamp}.tcl"
        self.generate_optimization_tcl(str(tcl_path))
        
        # Generate HTML report
        html_path = output_dir / f"timing_analysis_{timestamp}.html"
        self.generate_html_report(str(html_path))
        
        # Log summary
        logger.info(f"Timing analysis completed:")
        logger.info(f"  - Total paths analyzed: {len(self.timing_paths)}")
        logger.info(f"  - Violations found: {len(self.violations)}")
        logger.info(f"  - Critical violations: {len([v for v in self.violations if v.severity == 'critical'])}")
        logger.info(f"  - Reports generated in: {output_dir}")

def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(description="Enterprise FPGA Timing Analysis Tool")
    parser.add_argument("--project-root", required=True, help="Path to FPGA project root directory")
    parser.add_argument("--timing-report", required=True, help="Path to timing analysis report")
    parser.add_argument("--clock-report", help="Path to clock utilization report")
    parser.add_argument("--config", help="Path to custom configuration file")
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = EnterpriseTimingAnalyzer(args.project_root, args.config)
    
    # Run analysis
    analyzer.run_analysis(args.timing_report, args.clock_report)
    
    logger.info("Enterprise timing analysis completed successfully!")

if __name__ == "__main__":
    main()