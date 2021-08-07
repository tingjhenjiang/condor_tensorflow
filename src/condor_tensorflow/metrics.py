import tensorflow as tf
from tensorflow.keras import backend as K
from .activations import ordinal_softmax


class MeanAbsoluteErrorLabels(tf.keras.metrics.Metric):
  """Computes mean absolute error for ordinal labels."""

  def __init__(self, name="mean_absolute_error_labels",
                     **kwargs):
    """Creates a `MeanAbsoluteErrorLabels` instance."""
    super(MeanAbsoluteErrorLabels, self).__init__(name=name, **kwargs)
    self.maes = self.add_weight(name='maes', initializer='zeros')
    self.count = self.add_weight(name='count', initializer='zeros')

  def update_state(self, y_true, y_pred, sample_weight=None):
    """Computes mean absolute error for ordinal labels.

    Args:
      y_true: Cumulatiuve logits from CondorOrdinal layer.
      y_pred: CondorOrdinal Encoded Labels.
      sample_weight (optional): Not implemented.
    """

    if sample_weight:
      raise NotImplementedError

    # Predict the label as in Cao et al. - using cumulative probabilities
    cum_probs = tf.math.cumprod(tf.math.sigmoid(y_pred), axis = 1)# tf.map_fn(tf.math.sigmoid, y_pred)

    # Calculate the labels using the style of Cao et al.
    above_thresh = tf.map_fn(lambda x: tf.cast(x > 0.5, tf.float32), cum_probs)

    # Sum across columns to estimate how many cumulative thresholds are passed.
    labels_v2 = tf.reduce_sum(above_thresh, axis = 1)

    y_true = tf.cast(tf.reduce_sum(y_true,axis=1), y_pred.dtype)

    # remove all dimensions of size 1 (e.g., from [[1], [2]], to [1, 2])
    y_true = tf.squeeze(y_true)

    self.maes.assign_add(tf.reduce_sum(tf.abs(y_true - labels_v2)))
    self.count.assign_add(tf.cast(tf.size(y_true),tf.float32))

  def result(self):
    return tf.math.divide_no_nan(self.maes, self.count)

  def reset_states(self):
    """Resets all of the metric state variables at the start of each epoch."""
    K.batch_set_value([(v, 0) for v in self.variables])

  def get_config(self):
    """Returns the serializable config of the metric."""
    config = {}
    base_config = super().get_config()
    return {**base_config, **config}


class SparseMeanAbsoluteErrorLabels(MeanAbsoluteErrorLabels):
  """Computes mean absolute error for ordinal labels."""

  def __init__(self, name="mean_absolute_error_labels",
                     **kwargs):
    """Creates a `MeanAbsoluteErrorLabels` instance."""
    super().__init__(name=name, **kwargs)

  def update_state(self, y_true, y_pred, sample_weight=None):
    """Computes mean absolute error for ordinal labels.

    Args:
      y_true: Cumulatiuve logits from CondorOrdinal layer.
      y_pred: CondorOrdinal Encoded Labels.
      sample_weight (optional): Not implemented.
    """

    if sample_weight:
      raise NotImplementedError

    # Predict the label as in Cao et al. - using cumulative probabilities
    cum_probs = tf.math.cumprod(tf.math.sigmoid(y_pred), axis = 1)# tf.map_fn(tf.math.sigmoid, y_pred)

    # Calculate the labels using the style of Cao et al.
    above_thresh = tf.map_fn(lambda x: tf.cast(x > 0.5, tf.float32), cum_probs)

    # Sum across columns to estimate how many cumulative thresholds are passed.
    labels_v2 = tf.reduce_sum(above_thresh, axis = 1)

    y_true = tf.cast(y_true, y_pred.dtype)

    # remove all dimensions of size 1 (e.g., from [[1], [2]], to [1, 2])
    y_true = tf.squeeze(y_true)

    self.maes.assign_add(tf.reduce_sum(tf.abs(y_true - labels_v2)))
    self.count.assign_add(tf.cast(tf.size(y_true),tf.float32))


"""
# WIP
def MeanAbsoluteErrorLabels_v2(y_true, y_pred):
  # There will be num_classes - 1 cumulative logits as columns of the tensor.
  num_classes = y_pred.shape[1] + 1
  probs = logits_to_probs(y_pred, num_classes)

# RootMeanSquaredErrorLabels
"""

class EarthMoversDistanceLabels(tf.keras.metrics.Metric):
  """Computes earth movers distance for ordinal labels."""

  def __init__(self,num_classes,
                    name="earth_movers_distance_labels",
                    **kwargs):
    """Creates a `EarthMoversDistanceLabels` instance."""
    super().__init__(name=name, **kwargs)
    self.emds = self.add_weight(name='emds', initializer='zeros')
    self.count = self.add_weight(name='count', initializer='zeros')
    self.num_classes = tf.constant(num_classes,dtype=tf.float32)
    self.condor_encoded = condor_encoded

  def update_state(self, y_true, y_pred, sample_weight=None):
    """Computes mean absolute error for ordinal labels.

    Args:
      y_true: Cumulatiuve logits from CondorOrdinal layer.
      y_pred: CondorOrdinal Encoded Labels.
      sample_weight (optional): Not implemented.
    """

    if sample_weight:
      raise NotImplementedError

    cum_probs = ordinal_softmax(y_pred) #tf.math.cumprod(tf.math.sigmoid(y_pred), axis = 1)# tf.map_fn(tf.math.sigmoid, y_pred)

    if self.condor_encoded:
        y_true = tf.cast(tf.reduce_sum(y_true,axis=1), y_pred.dtype)
    else:
        y_true = tf.cast(y_true, y_pred.dtype)

    # remove all dimensions of size 1 (e.g., from [[1], [2]], to [1, 2])
    y_true = tf.squeeze(y_true)

    y_dist = tf.map_fn(fn=lambda y: tf.abs(y-tf.range(self.num_classes)),
                       elems=y_true)

    self.emds.assign_add(tf.reduce_sum(tf.math.multiply(y_dist,cum_probs)))
    self.count.assign_add(tf.cast(tf.size(y_true),tf.float32))

  def result(self):
    return tf.math.divide_no_nan(self.emds, self.count)

  def reset_states(self):
    """Resets all of the metric state variables at the start of each epoch."""
    K.batch_set_value([(v, 0) for v in self.variables])

  def get_config(self):
    """Returns the serializable config of the metric."""
    config = {"num_classes": self.num_classes}
    base_config = super().get_config()
    return {**base_config, **config}


class EarthMoversDistanceLabels(tf.keras.metrics.Metric):
  """Computes earth movers distance for ordinal labels."""

  def __init__(self,num_classes,
                    **kwargs):
    """Creates a `EarthMoversDistanceLabels` instance."""
    super().__init__(num_classes, **kwargs)

  def update_state(self, y_true, y_pred, sample_weight=None):
    """Computes mean absolute error for ordinal labels.

    Args:
      y_true: Cumulatiuve logits from CondorOrdinal layer.
      y_pred: Sparse Labels with values in {0,1,...,num_classes-1}
      sample_weight (optional): Not implemented.
    """

    if sample_weight:
      raise NotImplementedError

    cum_probs = ordinal_softmax(y_pred) #tf.math.cumprod(tf.math.sigmoid(y_pred), axis = 1)# tf.map_fn(tf.math.sigmoid, y_pred)

    y_true = tf.cast(y_true, y_pred.dtype)

    # remove all dimensions of size 1 (e.g., from [[1], [2]], to [1, 2])
    y_true = tf.squeeze(y_true)

    y_dist = tf.map_fn(fn=lambda y: tf.abs(y-tf.range(self.num_classes)),
                       elems=y_true)

    self.emds.assign_add(tf.reduce_sum(tf.math.multiply(y_dist,cum_probs)))
    self.count.assign_add(tf.cast(tf.size(y_true),tf.float32))

