
Lasagna ingredients

The "ingredients" are the elements which are added to plot axes. 
Ingredients include things such as:
 - Image stacks
 - Sparse points
 - Tree structures

To aid flexbility, the core lasagna application doesn't know how to
plot anything. Instead, it each loaded plot element is stored in an
object (an ingredient) that contains all the relevant data properties
associated with the object, including how to plot it. Each ingredient
is a class and each class is defined by a single Python file in this
directory. 

All classes must be descriptive lowercase names. 


