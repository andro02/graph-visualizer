# Graph-visualizer

## Team members
* Andrija Slović, SV12/2021
* Ana Španović, SV48/2021
* Vojkan Marković SV65/2021

## Dev project setup
To get started on project development, do the following after cloning the repository:

1. Create a virtual environment for the whole project in a folder called venv:
```shell
  python3 -m venv venv
```

2. Activate the virtual environment:
* On Linux / macOS:
```shell
  source venv/bin/activate
```

* On Windows:
```shell
  .\venv\Scripts\Activate
```

3. Upgrade pip
```shell
  python -m pip install --upgrade pip
```

4. Install requirements
```shell
  pip install -r requirements.txt
```

5. Run webapp
```shell
  python .\graph_explorer\graph_explorer_package\manage.py makemigrations
  python .\graph_explorer\graph_explorer_package\manage.py migrate
  python .\graph_explorer\graph_explorer_package\manage.py runserver
```