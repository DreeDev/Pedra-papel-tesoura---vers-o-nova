# Rock, paper, scissors
Small game to demonstrate the usage of websockets on a simple game. 

## Run app on dev mode
- Remove patch on `app.py`
```python
# import eventlet
# eventlet.monkey_patch()
```
```bash
flask --app app.py --debug run --port 8000
```

## Run app on prod mode
- Add monkey patch on `app.py`
```python
import eventlet
eventlet.monkey_patch()
```

```bash
gunicorn --worker-class eventlet -w 1 app:app
```