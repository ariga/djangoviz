# djangoviz

Visualize DjangoViz schemas with beautiful ERDs on [atlasgo.cloud](https://gh.atlasgo.cloud)

![alt text](https://entgo.io/images/assets/erd/edges-quick-summary.png)


## Installation

1. Install the `djangoviz` package:

```bash
pip install djangoviz
```

## Configuration

2. Add `djangoviz` to your Django project's `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'djangoviz',
    ...
]
```

## Usage

3. Generate the visualization by running the `djangoviz` management command:

```bash
python manage.py djangoviz
```

This command will create a visual representation of your projects database schema using Atlas Cloud. You can now easily view and explore the relationships between your models.

**Note**: Ensure that your Django project is properly configured and connected to a database before running the `djangoviz` command.