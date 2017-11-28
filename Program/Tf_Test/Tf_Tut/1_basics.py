import tensorflow as tf

# Fundamental
node1 = tf.constant(3.0, tf.float32)
node2 = tf.constant(4.0)
print(node1, node2)

"""
sess = tf.Session()
print(sess.run([node1, node2]))
sess.close()
"""

with tf.Session() as sess:
    print(sess.run([node1, node2]))

################################################################################
# Tensors and flow - with tensorboard
a = tf.constant(5)
b = tf.constant(6)
c = a * b

#File_Writer = tf.summary.FileWriter("C:\\Users\\WillG\\Desktop\\NEA\\Program\\Tf_Test\\Tf_Tut\\graph", sess.graph)
"""
To access this file writer
    - Cmd -> cd to Tf_Test (one higher)
    - tensorboard --logdir="Tf_Tut"
    - localhost:6006
"""

with tf.Session() as sess:
    print(sess.run(c))
################################################################################
# Placeholders
a = tf.placeholder(tf.float32)
b = tf.placeholder(tf.float32)
adder = a + b
with tf.Session() as sess:
    oup = sess.run(adder, {a:[1,3], b:[2,4]})
    print(oup)

################################################################################
#Variables
a = tf.Variable([.3], tf.float32)
b = tf.Variable([-.3], tf.float32)
c = tf.placeholder(tf.float32)

linear_model = a * c + b
init = tf.global_variables_initializer() # initialises all the variables

y = tf.placeholder(tf.float32) #placeholder for expected value
sq_deltas = tf.square(y - linear_model) # delta vector
loss = tf.reduce_sum(sq_deltas) # sum all values in sq_deltas

optimizer = tf.train.GradientDescentOptimizer(0.01)
train = optimizer.minimize(loss)

with tf.Session() as sess:
    sess.run(init)
    oup = sess.run(linear_model, {c:[1,2,3,4]})
    oup_loss = sess.run(loss, {c:[1,2,3,4], y:[0,-1,-2,-3]})
    print(oup)
    print(oup_loss)

    for i in range(1000):
        sess.run(train, {c:[1,2,3,4], y:[0,-1,-2,-3]})
    print(sess.run([a, b]))

################################################################################
