# VertexAI Session Service Evaluation Suite

A comprehensive testing framework for evaluating the VertexAI session service implementation, agent behavior, and performance characteristics.

## Overview

This evaluation suite provides three main categories of tests:

### 🔧 Session Service Evaluations (`session_evals.py`)

- **Basic Session Operations**: Create, retrieve, delete sessions
- **Multi-User Isolation**: Ensure sessions are properly isolated between users
- **State Persistence**: Verify session state is maintained across interactions
- **Error Handling**: Test graceful handling of invalid operations
- **Message Flow**: End-to-end message sending and receiving

### 🤖 Agent Behavior Evaluations (`agent_evals.py`)

- **Simulation Guidance Scenarios**: Test agent's ability to guide users through simulations
- **Response Quality**: Analyze response relevance, helpfulness, and accuracy
- **Consistency**: Ensure consistent responses across sessions
- **Context Awareness**: Verify agent maintains context throughout conversations
- **Specialized Scenarios**: Beginner onboarding, troubleshooting, advanced features

### ⚡ Performance Evaluations (`performance_evals.py`)

- **Response Time Distribution**: Measure response times for different message types
- **Concurrent Session Handling**: Test multiple simultaneous users
- **Session Creation Speed**: Benchmark session initialization performance
- **Large State Operations**: Test handling of sessions with substantial state data
- **Burst Load Handling**: Evaluate performance under rapid message bursts

## Quick Start

### Run All Evaluations

```bash
# From project root
python -m evals.run_all_evals
```

### Run Individual Suites

```bash
# Session functionality tests
python -m evals.session_evals

# Agent behavior tests
python -m evals.agent_evals

# Performance benchmarks
python -m evals.performance_evals
```

## Prerequisites

Before running evaluations, ensure:

1. **Environment Variables**: Set required environment variables:

   ```bash
   export PROJECT_ID=your_project_id
   export LOCATION=us-central1
   export REASONING_ENGINE_ID=your_engine_id
   ```

2. **Service Account**: Ensure `taajirah-agents-service-account.json` is in place

3. **Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Evaluation Structure

```
evals/
├── __init__.py              # Package initialization
├── README.md               # This documentation
├── session_evals.py        # Session service functionality tests
├── agent_evals.py          # Agent behavior and quality tests
├── performance_evals.py    # Performance and scalability tests
└── run_all_evals.py       # Master test runner with reporting
```

## Understanding Results

### Test Status Indicators

- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed (check error details)
- ⚠️ **PARTIAL**: Some issues detected but not critical

### Performance Metrics

- **Response Time**: Average time for agent responses
- **Success Rate**: Percentage of successful operations
- **Quality Score**: 0-1 rating of agent response quality
- **Concurrency**: Number of simultaneous operations handled

### Report Generation

The evaluation suite automatically generates:

1. **Console Output**: Real-time progress and summary
2. **JSON Report**: Detailed results saved to `evals/eval_report_TIMESTAMP.json`
3. **Metrics**: Performance benchmarks and quality scores

## Evaluation Scenarios

### Session Service Tests

- Create/retrieve/delete basic operations
- Multi-user session isolation
- State persistence across messages
- Error handling for invalid inputs
- Session listing and management

### Agent Behavior Tests

- **Beginner Onboarding**: How well the agent helps new users
- **Troubleshooting**: Problem acknowledgment and solution offering
- **Advanced Features**: Handling of complex configuration requests
- **Progress Tracking**: Monitoring and status reporting capabilities
- **Completion Flow**: End-of-simulation guidance

### Performance Tests

- **Response Time Distribution**: Short/medium/long message handling
- **Concurrent Sessions**: Multiple users simultaneously
- **Session Creation Speed**: Initialization performance
- **Large State Handling**: Sessions with substantial data
- **Burst Load**: Rapid successive requests

## Interpreting Quality Scores

Agent responses are evaluated on:

- **Keyword Relevance**: Presence of expected terms
- **Response Length**: Appropriate verbosity
- **Helpfulness**: Actionable guidance provided
- **Context Awareness**: Understanding of user's situation

Quality scores range from 0.0 to 1.0:

- **0.8-1.0**: Excellent responses
- **0.6-0.8**: Good responses with minor issues
- **0.4-0.6**: Adequate but could be improved
- **0.0-0.4**: Poor responses requiring attention

## Performance Benchmarks

### Target Performance Criteria

- **Average Response Time**: < 5 seconds
- **Maximum Response Time**: < 10 seconds
- **Session Creation**: < 2 seconds
- **Concurrent User Success Rate**: > 90%
- **Burst Load Success Rate**: > 80%

### Scaling Characteristics

The evaluations test:

- Up to 5 concurrent users
- Sessions with 100+ state parameters
- Burst loads of 8 rapid messages
- Large state retrievals and updates

## Troubleshooting

### Common Issues

**Authentication Errors**:

- Verify service account file exists
- Check PROJECT_ID and LOCATION environment variables
- Ensure proper GCP permissions

**Performance Issues**:

- Check network connectivity to VertexAI
- Verify reasoning engine is active
- Monitor GCP quotas and limits

**Test Failures**:

- Review error messages in console output
- Check detailed JSON report for specifics
- Verify agent is responding appropriately

### Debug Mode

Run individual tests for detailed debugging:

```bash
# Enable verbose output
export PYTHONPATH=.
python evals/session_evals.py
```

## Extending Evaluations

### Adding New Test Scenarios

1. Create test methods in appropriate evaluation class
2. Follow naming convention: `eval_[test_name]`
3. Return standardized result dictionary
4. Add cleanup for any created resources

### Custom Evaluation Criteria

Modify success criteria in evaluation classes:

- Update `success_criteria` dictionaries
- Adjust performance thresholds
- Add new quality metrics

## Continuous Integration

This evaluation suite is designed for:

- Pre-deployment testing
- Performance regression detection
- Agent behavior validation
- System health monitoring

Integrate with CI/CD pipelines by:

1. Running `python -m evals.run_all_evals`
2. Checking exit codes (0 = success, 1 = failures)
3. Parsing JSON reports for detailed metrics
4. Setting performance thresholds for automatic validation
