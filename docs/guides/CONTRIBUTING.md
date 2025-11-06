# Contributing to Laniakea Protocol 🌌

Thank you for your interest in contributing to Laniakea Protocol! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Bugs

1. **Search existing issues**: Check if the bug has already been reported
2. **Create a new issue**: Use the bug report template
3. **Provide details**: Include steps to reproduce, expected behavior, and environment
4. **Add logs**: Include relevant logs and error messages

### Suggesting Features

1. **Check roadmap**: Review if the feature aligns with our roadmap
2. **Open a discussion**: Start with a GitHub Discussion
3. **Create an issue**: Use the feature request template
4. **Provide use cases**: Explain why this feature is needed

### Code Contributions

#### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git
- Familiarity with FastAPI, asyncio, and blockchain concepts

#### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/laniakea-protocol.git
   cd laniakea-protocol
   ```

2. **Set Up Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   pre-commit install
   ```

3. **Start Development Services**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

#### Development Workflow

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make Changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation

3. **Run Tests**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=src --cov-report=html

   # Run linting
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create Pull Request on GitHub
   ```

## 📝 Coding Standards

### Code Style

We use the following tools and standards:

- **Black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **isort**: Import sorting

#### Installation

```bash
pip install black flake8 mypy isort
```

#### Usage

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Sort imports
isort src/ tests/
```

### Code Quality Guidelines

#### 1. Python Code Style

```python
# Good: Use type hints
from typing import List, Dict, Optional

async def process_transactions(
    transactions: List[Dict[str, Any]],
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Process a list of transactions."""
    if limit is not None:
        transactions = transactions[:limit]
    
    processed = []
    for tx in transactions:
        processed.append(await validate_transaction(tx))
    
    return processed

# Bad: No type hints, unclear naming
def process_txs(txs, l=None):
    p = []
    for tx in txs[:l] if l else txs:
        p.append(validate_tx(tx))
    return p
```

#### 2. Documentation

```python
class BlockchainProcessor:
    """Handles blockchain processing operations.
    
    This class provides methods for processing transactions,
    validating blocks, and maintaining blockchain state.
    
    Attributes:
        chain: The blockchain instance
        validator: Transaction validator
        logger: Logger instance
    """
    
    def __init__(self, chain: Blockchain, validator: TransactionValidator):
        """Initialize the blockchain processor.
        
        Args:
            chain: Blockchain instance to process
            validator: Validator for transaction verification
        """
        self.chain = chain
        self.validator = validator
        self.logger = logging.getLogger(__name__)
    
    async def process_block(self, block: Block) -> bool:
        """Process a new block.
        
        Validates the block, processes transactions, and updates the chain.
        
        Args:
            block: The block to process
            
        Returns:
            True if block was successfully processed, False otherwise
            
        Raises:
            ValidationError: If block validation fails
            ProcessingError: If transaction processing fails
        """
        # Implementation here
        pass
```

#### 3. Error Handling

```python
# Good: Specific exceptions with context
try:
    result = await process_transaction(transaction)
except ValidationError as e:
    logger.error(f"Transaction validation failed: {e}")
    raise TransactionError(f"Invalid transaction {transaction.id}: {e}")
except ProcessingError as e:
    logger.error(f"Transaction processing failed: {e}")
    raise

# Bad: Generic exceptions, no context
try:
    result = process_transaction(transaction)
except Exception:
    logger.error("Something went wrong")
    return None
```

#### 4. Testing

```python
# Good: Comprehensive tests with fixtures
import pytest
from unittest.mock import Mock, patch

class TestBlockchainProcessor:
    
    @pytest.fixture
    def processor(self):
        chain = Mock()
        validator = Mock()
        return BlockchainProcessor(chain, validator)
    
    @pytest.fixture
    def sample_block(self):
        return Block(
            id="test_block",
            transactions=[Transaction(id="tx1"), Transaction(id="tx2")]
        )
    
    async def test_process_block_success(self, processor, sample_block):
        """Test successful block processing."""
        processor.validator.validate_block.return_value = True
        processor.chain.add_block.return_value = True
        
        result = await processor.process_block(sample_block)
        
        assert result is True
        processor.validator.validate_block.assert_called_once_with(sample_block)
        processor.chain.add_block.assert_called_once_with(sample_block)
    
    async def test_process_block_validation_failure(self, processor, sample_block):
        """Test block processing with validation failure."""
        processor.validator.validate_block.return_value = False
        
        with pytest.raises(ValidationError):
            await processor.process_block(sample_block)
```

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_blockchain.py
│   ├── test_consensus.py
│   └── test_ai_core.py
├── integration/            # Integration tests
│   ├── test_api.py
│   ├── test_websocket.py
│   └── test_database.py
├── performance/            # Performance tests
│   ├── test_load.py
│   └── test_stress.py
└── conftest.py            # Test configuration
```

### Test Requirements

1. **Coverage**: Maintain 95%+ test coverage
2. **Unit Tests**: Test individual components in isolation
3. **Integration Tests**: Test component interactions
4. **Performance Tests**: Validate performance requirements
5. **Security Tests**: Verify security measures

### Running Tests

```bash
# All tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Performance tests
pytest tests/performance/

# Specific test file
pytest tests/unit/test_blockchain.py::TestBlockchain::test_add_block

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

## 📚 Documentation

### Documentation Standards

1. **README.md**: Project overview and quick start
2. **API Documentation**: Complete API reference
3. **Architecture Docs**: System design and components
4. **Development Guide**: Setup and contribution guide
5. **Deployment Guide**: Production deployment instructions

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up to date
- Use consistent formatting

## 🚀 Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Code Quality**
   - [ ] All tests pass
   - [ ] Code coverage ≥ 95%
   - [ ] No linting errors
   - [ ] Documentation updated

2. **Security**
   - [ ] Security scan passed
   - [ ] Dependencies updated
   - [ ] Vulnerabilities fixed

3. **Performance**
   - [ ] Performance tests pass
   - [ ] Benchmarks updated
   - [ ] No regressions

4. **Release**
   - [ ] Version bumped
   - [ ] Changelog updated
   - [ ] Tag created
   - [ ] Release published

## 🏆 Recognition

### Contributor Recognition

- **Contributors**: Listed in README.md
- **Top Contributors**: Special recognition in releases
- **Community Awards**: Monthly contributor awards
- **Swag**: Merchandise for significant contributions

### Contribution Types

- **Code**: New features, bug fixes, improvements
- **Documentation**: Guides, tutorials, API docs
- **Design**: UI/UX, graphics, diagrams
- **Testing**: Test cases, bug reports
- **Community**: Support, discussions, outreach

## 📞 Getting Help

### Communication Channels

- **Discord**: [Join our Discord](https://discord.gg/laniakea)
- **GitHub Discussions**: [Start a discussion](https://github.com/QalamHipHop/laniakea-protocol/discussions)
- **Email**: dev@laniakea.io

### Resources

- **Documentation**: [docs.laniakea.io](https://docs.laniakea.io)
- **API Reference**: [api.laniakea.io](https://api.laniakea.io)
- **Tutorials**: [tutorials.laniakea.io](https://tutorials.laniakea.io)

## 📋 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of:

- Age, body size, disability, ethnicity, gender identity
- Level of experience, education, socioeconomic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive Behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable Behavior:**
- Harassment, trolling, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing private information
- Unprofessional conduct

### Enforcement

Project maintainers have the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned with this Code of Conduct.

## 🙏 Thank You

Thank you for contributing to Laniakea Protocol! Your contributions help make this project better for everyone.

---

For any questions or concerns, please don't hesitate to reach out to our team.