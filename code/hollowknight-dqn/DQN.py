import tensorflow as tf
import numpy as np

class ActModel(tf.keras.Model):
    def __init__(self, act_dim):
        super(ActModel, self).__init__()
        self.dense1 = tf.keras.layers.Dense(64, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.dense3 = tf.keras.layers.Dense(act_dim)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        return x

class MoveModel(tf.keras.Model):
    def __init__(self, move_dim):
        super(MoveModel, self).__init__()
        self.dense1 = tf.keras.layers.Dense(64, activation='relu')
        self.dense2 = tf.keras.layers.Dense(64, activation='relu')
        self.dense3 = tf.keras.layers.Dense(move_dim)

    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        x = self.dense3(x)
        return x

class DQN:
    def __init__(self, model, gamma=0.9, learning_rate=0.0001):
        self.model = model
        self.act_dim = model.act_dim
        self.move_dim = model.move_dim
        self.act_model = ActModel(self.act_dim)
        self.move_model = MoveModel(self.move_dim)
        self.gamma = gamma
        self.lr = learning_rate

        # train the model
        self.act_optimizer = tf.keras.optimizers.Adam(learning_rate=self.lr)
        self.act_loss_func = tf.keras.losses.MeanSquaredError()

        self.move_optimizer = tf.keras.optimizers.Adam(learning_rate=self.lr)
        self.move_loss_func = tf.keras.losses.MeanSquaredError()

    @tf.function
    def act_train_step(self, action, features, labels):
        with tf.GradientTape() as tape:
            predictions = self.act_model(features, training=True)
            enum_action = list(enumerate(action))
            pred_action_value = tf.gather_nd(predictions, indices=enum_action)
            loss = self.act_loss_func(labels, pred_action_value)
        gradients = tape.gradient(loss, self.act_model.trainable_variables)
        self.act_optimizer.apply_gradients(zip(gradients, self.act_model.trainable_variables))
        self.model.act_loss.append(loss)

    @tf.function
    def move_train_step(self, move, features, labels):
        with tf.GradientTape() as tape:
            predictions = self.move_model(features, training=True)
            enum_move = list(enumerate(move))
            pred_move_value = tf.gather_nd(predictions, indices=enum_move)
            loss = self.move_loss_func(labels, pred_move_value)
        gradients = tape.gradient(loss, self.move_model.trainable_variables)
        self.move_optimizer.apply_gradients(zip(gradients, self.move_model.trainable_variables))
        self.model.move_loss.append(loss)

    def act_learn(self, obs, action, reward, next_obs, terminal,epochs=1):
        for _ in tf.range(1, epochs+1):
            self.act_train_step(action, obs, reward)
        self.act_global_step += 1

    def move_learn(self, obs, move, reward, next_obs, terminal, epochs=1):
        for _ in tf.range(1, epochs+1):
            self.move_train_step(move, obs, reward)
        self.move_global_step += 1

    def act_replace_target(self):
        for i, l in enumerate(self.model.act_target_model.get_layer(index=1).
                              get_layer(index=0).
                              get_layer(index=0).
                              get_layers()):
            l.set_weights(self.act_model.get_layer(index=1).
                          get_layer(index=0).
                          get_layer(index=0).
                          get_layer(index=i).
                          get_weights())
        for i, l in enumerate(self.model.act_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layers()):
            l.set_weights(self.act_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layer(index=i).get_weights())

    def move_replace_target(self):
        for i, l in enumerate(self.model.move_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=0).get_layers()):
            l.set_weights(self.move_model.get_layer(index=1).get_layer(index=0).get_layer(index=0).get_layer(index=i).get_weights())
        for i, l in enumerate(self.model.move_target_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layers()):
            l.set_weights(self.move_model.get_layer(index=1).get_layer(index=0).get_layer(index=1).get_layer(index=i).get_weights())