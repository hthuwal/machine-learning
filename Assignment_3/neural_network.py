import numpy as np
import random
from scipy.special import expit


class Layer(object):
    def __init__(self, num_units, activation, num_units_in_prev_layer):
        self.num_units = num_units
        self.activation = activation
        self.outputs = np.zeros(num_units)
        self.thetas = np.random.randn(num_units, num_units_in_prev_layer) * 0.001
        self.inputs = None
        self.gradients = None

    def __repr__(self):
        return "(Num_Units: %d, Activation_function: %s, Thetas shape: %s)" % (self.num_units, self.activation, self.thetas.shape)


class Neural_Network(object):
    def __init__(self, num_inputs, num_hidden_units_list, activation):
        np.random.seed(64550)
        random.seed(93128)
        if len(num_hidden_units_list) == 0:
            self.hidden_layer_sizes = num_hidden_units_list
            self.layers = [Layer(2, "sigmoid", num_inputs)]
            self.num_layers = len(num_hidden_units_list) + 1
        else:
            self.hidden_layer_sizes = num_hidden_units_list
            self.num_layers = len(num_hidden_units_list) + 1
            self.layers = [Layer(num_hidden_units_list[0], activation, num_inputs)]

            for i in range(1, len(num_hidden_units_list)):
                layer = Layer(num_hidden_units_list[i], activation, num_hidden_units_list[i - 1])
                self.layers.append(layer)

            layer = Layer(2, "sigmoid", num_hidden_units_list[-1])
            self.layers.append(layer)

    def forward_pass(self, inp):
        inp = np.matrix(inp)
        self.layers[0].inputs = inp
        self.layers[0].netj = inp @ (np.matrix(self.layers[0].thetas).T)
        self.layers[0].outputs = self.nonlinearity(self.layers[0].netj, self.layers[0].activation)

        for i in range(1, self.num_layers):
            layer = self.layers[i]
            layer.inputs = self.layers[i - 1].outputs
            layer.netj = layer.inputs @ (np.matrix(self.layers[i].thetas).T)
            layer.outputs = self.nonlinearity(layer.netj, layer.activation)

    def backward_pass(self, gold_labels):
        # for output layer
        out_layer = self.layers[-1]
        gold = np.zeros((len(gold_labels), out_layer.num_units))  # convert gold_labels in o/p format
        for i in range(len(gold_labels)):
            gold[i][gold_labels[i]] = 1

        gold = np.matrix(gold)
        out_layer.grad_wrt_netj = -np.multiply((gold - out_layer.outputs), self.gnl(out_layer.netj, out_layer.activation))
        out_layer.gradients = (out_layer.grad_wrt_netj.T) @ out_layer.inputs

        # for other layers
        for i in range(self.num_layers - 2, -1, -1):
            layer = self.layers[i]
            next_layer = self.layers[i + 1]
            layer.grad_wrt_netj = np.multiply((next_layer.grad_wrt_netj @ next_layer.thetas), self.gnl(layer.netj, layer.activation))
            layer.gradients = (layer.grad_wrt_netj.T) @ layer.inputs

    def nonlinearity(self, output, activation):
        if activation == "sigmoid":
            return self.sigmoid(output)
        if activation == "ReLU":
            return self.relu(output)

    def gnl(self, netj, activation):
        if activation == "sigmoid":
            oj = self.sigmoid(netj)
            return np.multiply(oj, (1 - oj))
        if activation == "ReLU":
            temp = np.matrix(netj)
            temp[temp < 0] = 0
            temp[temp >= 0] = 1
            return temp

    def update_thetas(self, eeta, momentum=5):
        for layer in self.layers:
            # print("Updating", np.max(layer.gradients))
            layer.thetas = layer.thetas - eeta * (layer.gradients)

    def error(self, gold_labels):
        out_layer = self.layers[-1]
        gold = np.zeros((len(gold_labels), out_layer.num_units))  # convert gold_labels in o/p format
        for i in range(len(gold_labels)):
            gold[i][gold_labels[i]] = 1

        gold = np.matrix(gold)

        err = gold - out_layer.outputs
        err = np.sum(np.square(err)) / 2
        return err

    def train(self, data, labels, eeta=0.01, batch_size=100, max_iter=1000, threshold=1e-4, decay=False):
        # pdb.set_trace()
        zip_data = list(zip(data, labels))
        it = 1
        random.shuffle(zip_data)
        dev_data, dev_labels = zip(*zip_data[0: int(0.1 * len(zip_data))])
        self.forward_pass(dev_data)
        old_error = self.error(dev_labels)
        epochs = 1
        lr = eeta
        while(epochs <= max_iter):
            dev_data, dev_labels = zip(*zip_data[0: int(0.1 * len(zip_data))])
            for i in range(int(0.1 * len(zip_data)), len(zip_data), batch_size):
                batch = zip_data[i: i + batch_size]
                x, y = zip(*batch)
                self.forward_pass(x)
                self.backward_pass(y)
                if decay:
                    self.update_thetas(lr / batch_size)
                else:
                    self.update_thetas(lr)

                it += 1
                if decay:
                    lr = eeta * (1 / np.sqrt(it))
            self.forward_pass(dev_data)
            error = self.error(dev_labels)
            print("\rEpoch: %d, Error: %f old_error: %f" % (epochs, error, old_error), end=" ")

            if np.abs(old_error - error) < threshold:
                break
            old_error = error
            epochs += 1
            # random.shuffle(zip_data)

        print("\n")

    def predict(self, inp):
        self.forward_pass(inp)
        out = self.layers[-1].outputs
        return np.array(out.argmax(axis=1)).flatten()
    """ Activation Functions """

    def relu(self, output):
        """[rectified linear unit]
        f(x)=max(x,0)
        """
        output[output < 0] = 0
        return output

    def sigmoid(self, output):
        """
        f(x) = 1 / (1 + exp(x))
        """
        # TODO check for correctness
        return expit(output)

    def __repr__(self):
        representation = ""
        for i, layer in enumerate(self.layers):
            temp = "Layer %d - %s\n" % (i, layer)
            representation += temp
        return representation

    def print_outputs(self):
        for layer in self.layers:
            print(layer.outputs)

    def print_graidents(self):
        for layer in self.layers:
            print(layer.gradients)


if __name__ == '__main__':
    batch = [[1, 2, 3], [4, 5, 6]]
    nn = Neural_Network(3, [5, 4], "ReLU")
    print(nn)
    nn.train(0.1, batch, [1, 0], batch_size=2, max_iter=10000)
