====================================
IDT: Individualized Discounting Task
====================================

The *IDT* is an adaptive individualized delay discounting task for functional magnetic resonance imaging as described in `Koffarnus et al. 2017 <http://www.sciencedirect.com/science/article/pii/S1053811917306717>`_. The corresponding statistical maps can be downloaded from `neurovault.org <https://neurovault.org/collections/GWAYZDJA/>`_.

Since the *IDT* is individualized, the out-of-scanner version needs to be performed first.

Install
-------
The *IDT* requires `Python <https://www.python.org/>`_, `NumPy <http://www.numpy.org/>`_, `Pygame <http://www.pygame.org>`_, `PyOpenGL <http://pyopengl.sourceforge.net/>`_ and `Vision Egg <http://visionegg.org/>`_.

We recommend installing `Python <https://www.python.org/>`_ and all dependencies by installing `Miniconda <https://conda.io/miniconda.html>`_ and by creating a virtual environment::

  conda create -n IDT python=2.7 numpy=1.8 pil
  source activate IDT
  pip install pygame pyopengl visionegg
