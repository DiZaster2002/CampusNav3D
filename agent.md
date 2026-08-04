En este documento se indican la salida estándar y la salida personalizada de las consultas realizadas sobre el proyecto CampusNav3D. Se añade el hecho de que todo código debe estar escrito en Python, y se incluye la estructura actual de carpetas y archivos para mayor facilidad a la hora de requerir archivos para completar las consultas.



La IA y modelo que consuma este documento deberá ser capaz de analizar la consulta del usuario previamente y aplicar el tipo de salida que corresponda con las necesidades del mismo. En ocasiones especiales, el usuario podrá ser el encargado de elegir el tipo de respuesta deseada variando entre la salida estándar y la personalizada.



**SALIDA ESTÁNDAR**



Esta respuesta se aplicará a aquellos pasos que avancen de manera significativa el desarrollo del proyecto, comúnmente asociada a inclusiones de código, adición de funcionalidades o auditorías.

Antes de proporcionar una salida estándar, se pedirá a través de un output breve la lista de archivos necesarios que no se encuentren en el contexto local de la conversación. Dados estos archivos en una consulta del usuario, se procederá a proporcionar la debida salida estándar.

**1.-** Gestión y Estrategia en GitHub/Git



Aquí se tratarán los pasos a realizar desde el último punto del curso del proyecto en el repositorio asociado en GitHub. También se darán indicaciones para un control de versiones con Git desde la terminal del entorno de trabajo, es decir, la terminal de VSCode.



Se hablará de:

* Si se debe hacer PR o no, sus títulos y descripciones con nomenclatura estándar (feat, fix, …)
* Creación de landmarks, issues, su numeración, títulos y descripciones con nomenclatura estándar.
* Creación, manejo o eliminación de ramas en el control de versiones del entorno de trabajo.



**2.-** Paso a paso Técnico



Aquí se dará al usuario una propuesta de código para progresar por el desarrollo del proyecto según se vaya avanzando. La salida serán bloques de código acompañados previamente por una ligera descripción del problema que resuelven. 



Se incluirá en cada bloque de código la ubicación y nombre del archivo en el que se deberá incluir este nuevo bloque de código.



Queda PROHIBIDO modificar la estructura del proyecto en este paso sin antes consultar al usuario sobre el cambio. Toda adición al proyecto no necesitará de confirmación, solo los cambios a lo ya existente en cuanto a estructura se refiere. Salidas como código nuevo, importaciones añadidas o corrección de funciones o procesos durante la marcha no necesitan de confirmación, pero deberán ser indicados con su debido comentario.



Cada bloque de código irá separado en partes en la salida, siendo cada parte correspondiente a un problema que solucione ese bloque. Como ejemplo, si una fase del desarrollo implica resolver 3 funcionalidades, y en cada función se deben modificar/crear 3 archivos, la salida se dividirá en 3 partes, una por funcionalidad, y se incluirán los bloques de código a añadir en cada archivo de cada funcionalidad.



**3.-** Acciones posteriores



Aquí se proporcionará al usuario maneras tangibles de comprobar los resultados de la salida proporcionada, ya sea por terminal de VSCode de Windows, o a través de las rutas API creadas en el proyecto.



Se darán los comandos necesarios para realizar acciones como levantar contenedores de Docker, poblar los modelos de datos con cURL, realizar migraciones para reconstruir modelos o contenedores, etc...


Existirá un apartado de resultado esperado, indicando al usuario la salida correcta de una ejecución del código proporcionado. 



Se incluirá un apartado de sugestión de información a incluir en el archivo README.md si las modificaciones o inclusiones de código de la consulta actual son merecedoras de ello o modifican algo significativo del mismo.



En caso de haber terminado una fase del desarrollo, o poder dar por concluida una issue, se proporcionarán los comandos a realizar junto con las descripciones o comentarios a incluir necesarios.

Por último, se hará una sugerencia de si es buen momento para crear tests de integración sobre lo implementado.



Para finalizar la salida estándar, se hará un breve resumen de lo implementado en lenguaje natural, y se propondrá el siguiente paso a tomar en el curso de desarrollo del proyecto, sea una nueva funcionalidad dentro de la misma fase, el paso a una auditoría, o la continuación a una nueva fase de desarrollo.




**SALIDA PERSONALIZADA**



Este tipo de salida se utilizará a discreción tanto de la IA como del usuario, siendo la IA quien tome la decisión de su uso en caso de no ser indicado en la consulta proporcionada por el usuario. Se utilizará generalmente para arreglos o modificaciones ligeras de código que no hagan avanzar en el desarrollo, que sirvan como resolución de dudas o correcciones de bloques de código de un tamaño menor.



En este tipo de salidas no se incluirán, a menos que el calibre de la modificación o corrección lo merezca:

* Acciones en GitHub/Git



El esquema a seguir de salida será idéntico en cualquier otro aspecto no mencionado en la lista.



**ESTRUCTURA DE CARPETAS Y ARCHIVOS**
```
CampusNav3D/
├── .github/
    ├── dependabot.yml
    ├──workflows/ci.yml
├── .venv/
    ├── ...
├── backend/
    ├── db.sqlite3
    ├── Dockerfile
    ├── manage.py
    ├── requirements.txt
    ├── core/
        ├── __init__.py
        ├── asgi.py
        ├── celery.py
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
    ├── examples/campus_sample.json
    ├── maps/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── factories.py
        ├── models.py
        ├── patterns.py
        ├── schemas.py
        ├── serializers.py
        ├── tasks.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        ├── management/commands/import_campus.py
        ├── migrations/
            ├── __init__.py
            ├── 0001_...
            ├── 0002_...
        ├── providers/
            ├── base.py
            ├── mock.py
    ├── spatial_plans/
├── benchmark/
├── docs/
├── frontend/
├── schemas/
├── test_img/
    ├── test1.png
    ├── ...
├── workers/
├── .env.example
├── .gitignore
├── agent.md
├── context.md
├── docker-compose.yml
├── LICENSE
├── README.md
```