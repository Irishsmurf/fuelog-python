Exceptions
==========

All exceptions raised by the library derive from :exc:`FuelogError`.

Hierarchy
---------

.. code-block:: text

   FuelogError
   ├── FuelogAPIError
   │   ├── FuelogAuthError        (HTTP 401)
   │   ├── FuelogForbiddenError   (HTTP 403)
   │   ├── FuelogNotFoundError    (HTTP 404)
   │   ├── FuelogValidationError  (HTTP 422)
   │   ├── FuelogRateLimitError   (HTTP 429)
   │   └── FuelogServerError      (HTTP 5xx)
   └── FuelogMCPError

Reference
---------

.. autoclass:: fuelog.FuelogError
   :members:
   :show-inheritance:

.. autoclass:: fuelog.FuelogAPIError
   :members:
   :show-inheritance:

.. autoclass:: fuelog.FuelogAuthError
   :show-inheritance:

.. autoclass:: fuelog.FuelogForbiddenError
   :show-inheritance:

.. autoclass:: fuelog.FuelogNotFoundError
   :show-inheritance:

.. autoclass:: fuelog.FuelogValidationError
   :show-inheritance:

.. autoclass:: fuelog.FuelogRateLimitError
   :show-inheritance:

.. autoclass:: fuelog.FuelogServerError
   :show-inheritance:

.. autoclass:: fuelog.FuelogMCPError
   :members:
   :show-inheritance:
