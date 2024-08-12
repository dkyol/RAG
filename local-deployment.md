# Techniques for Improving the Effectiveness of RAG Systems
### NVIDIA Deep Learning Institute

**This guide is only applicable if you intend to build this application locally,
outside of the DLI JupyterLab environment. Otherwise refer to `Lesson 00.ipynb` to 
get started with the course.**

The source code for the microservices launched in this course
can be found within their respective sub-directories, e.g. `chunking`

Within the DLI JupyterLab environment, users are expected to simply launch 
containers using the command `docker-compose up -d`. Refer to `Lesson 00.ipynb` 
for more guidance on how to do this.

Within the learning environment, these images have all been pre-built 
ahead of time. However, if you are interested in migrating this system to your local 
environment, you will need to build the images yourself before running the
`docker-compose up -d` command. You can do this by following the steps outlined here.

#### Build Base Image
```bash
cd base
bash build_image.sh
cd ..
```

#### Build Chunking Image
```bash
cd chunking
bash build_image.sh
cd ..
```

#### Build Router Image
```bash
cd router
bash build_image.sh
cd ..
```

#### Build Triton Image
*This is the only lengthy build process among the different microservices.*
Note that serving a local embedding model on Triton 
will require a local GPU with sufficient memory.
Follow steps outlined in `triton/README.md`


#### Build Judge Image
```bash
cd judge
bash build_image.sh
cd ..
```

#### Build Web Image
```bash
cd web
bash build_image.sh
cd ..
```

#### Edit `docker-compose.yml`

The next step is to modify `docker-compose.yml` so that the image 
names in the config generated for our JupyterLab environment)
match the image names we used when building the images.

For example, within `docker-compose.yml`, 
change the `image` field within `chunking` from 
`x-fx-60-v1-task1-chunking:v1.8.0` to `chunking`

**Important!** We did not have to build redis since we're using the official image, but don't forget to switch the image name for `redis` accordingly, from `x-fx-60-v1-task1-redis` to `redis/redis-stack:latest` 

#### (Optional) Use Mixtral through AI Foundation Endpoint instead of local Mixtral
If your local environment does not have the GPU memory needed for running 
Mixtral (~90 GB for half precision, ~45 GB for 8-bit) as we do in the course 
environment, follow the steps described in `Lesson 04.ipynb` to switch 
to making API calls to NVIDIA AI Foundations.