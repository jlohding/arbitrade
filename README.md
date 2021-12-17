# Arbitrade

This repository contains the codebase for my live algorithmic trading system. All behaviour is controlled via config files in ```/src/arbitrade/conf``` 

### Techology Stack
- Linux (Debian 10 VPS)
- Python >=3.9
- PostgreSQL==13.4
- ibapi==9.81.1.post1

### Current Features
- Automated futures roll, including spreads
- PostgreSQL integration with IB API with CRUD operations
- Automated crontab update to run program at asset(s) next market open 
- Modular strategy and asset configuration for multi-strategy portfolios via config files

### Roadmap / To do list
- [ ] Unit testing
- [ ] Documentation
- [ ] Setup scripts
- [ ] Execution algorithm module

### License
[GNU AGPLv3](https://choosealicense.com/licenses/agpl-3.0/)