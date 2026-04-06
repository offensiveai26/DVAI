# Contributing to DVAI

Thanks for your interest in DVAI! Here's how you can help.

## Ways to Contribute

- **Report bugs** - Open an issue with steps to reproduce
- **Suggest challenges** - Got an idea for a new attack scenario? Open an issue
- **Improve existing challenges** - Better simulation patterns, more attack vectors
- **Fix typos/docs** - PRs welcome
- **Add walkthroughs** - Help others learn by writing challenge solutions

## Development Setup

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Pull Request Guidelines

1. Fork the repo and create a branch from `main`
2. Test your changes locally (both backend and frontend)
3. Keep PRs focused - one feature or fix per PR
4. Update the README if you add new challenges

## Adding a New Challenge

1. Create a handler in `backend/app/challenges/<category>/`
2. Add the challenge entry in `backend/app/challenges/registry.py`
3. Use `from app.flags import get_flag` - never hardcode flags
4. Test all 3 difficulty levels
5. Write a fun story and good hints

## Code Style

- Python: follow existing patterns, use async handlers
- React: functional components, Tailwind for styling
- Keep it simple - minimal dependencies

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
