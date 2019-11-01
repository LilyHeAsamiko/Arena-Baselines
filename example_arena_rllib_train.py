from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
"""Simple example of setting up a multi-agent policy mapping.

Control the number of agents and policies via --num-agents and --num-policies.

This works with hundreds of agents and policies, but note that initializing
many TF policies will take some time.

Also, TF evals might slow down with large numbers of policies. To debug TF
execution, set the TF_TIMELINE_DIR environment variable.
"""

import argparse
import gym
import random

import ray
from ray import tune
from ray.rllib.models import Model, ModelCatalog
from ray.rllib.tests.test_multi_agent_env import MultiCartpole
from ray.tune.registry import register_env
from ray.rllib.utils import try_import_tf
from envs_layer import ArenaRllibEnv

from envs_layer import ArenaRllibEnv

tf = try_import_tf()

parser = argparse.ArgumentParser()

parser.add_argument("--num-agents", type=int, default=2)
parser.add_argument("--num-policies", type=int, default=2)
parser.add_argument("--num-iters", type=int, default=20)
parser.add_argument("--simple", action="store_true")


class CustomModel1(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        # Example of (optional) weight sharing between two different policies.
        # Here, we share the variables defined in the 'shared' variable scope
        # by entering it explicitly with tf.AUTO_REUSE. This creates the
        # variables for the 'fc1' layer in a global scope called 'shared'
        # outside of the policy's normal variable scope.
        with tf.variable_scope(
                tf.VariableScope(tf.AUTO_REUSE, "shared"),
                reuse=tf.AUTO_REUSE,
                auxiliary_name_scope=False):
            last_layer = tf.layers.dense(
                input_dict["obs"], 64, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(
            last_layer, 64, activation=tf.nn.relu, name="fc2")
        output = tf.layers.dense(
            last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer


class CustomModel2(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        # Weights shared with CustomModel1
        with tf.variable_scope(
                tf.VariableScope(tf.AUTO_REUSE, "shared"),
                reuse=tf.AUTO_REUSE,
                auxiliary_name_scope=False):
            last_layer = tf.layers.dense(
                input_dict["obs"], 64, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(
            last_layer, 64, activation=tf.nn.relu, name="fc2")
        output = tf.layers.dense(
            last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer


class CustomModel2(Model):
    def _build_layers_v2(self, input_dict, num_outputs, options):
        # Weights shared with CustomModel1
        with tf.variable_scope(
                tf.VariableScope(tf.AUTO_REUSE, "shared"),
                reuse=tf.AUTO_REUSE,
                auxiliary_name_scope=False):
            last_layer = tf.layers.dense(
                input_dict["obs"], 64, activation=tf.nn.relu, name="fc1")
        last_layer = tf.layers.dense(
            last_layer, 64, activation=tf.nn.relu, name="fc2")
        output = tf.layers.dense(
            last_layer, num_outputs, activation=None, name="fc_out")
        return output, last_layer


if __name__ == "__main__":
    args = parser.parse_args()
    ray.init()

    input('Windows: Ctrl_Z+Return')

    # Simple environment with `num_agents` independent cartpole entities
    # register_env("multi_cartpole", lambda _: MultiCartpole(args.num_agents))
    register_env("multi_cartpole", lambda _: ArenaRllibEnv())
    ModelCatalog.register_custom_model("model1", CustomModel1)
    ModelCatalog.register_custom_model("model2", CustomModel2)
    # single_env = MultiCartpole(args.num_agents)
    single_env = ArenaRllibEnv()
    obs_space = single_env.observation_space
    act_space = single_env.action_space

    print(single_env.reset())
    # {0: array([-0.02471631, -0.01529849,  0.00066952, -0.04968461]), 1: array([ 0.01979751,  0.00022062,  0.02034531, -0.04991479])}

    print(single_env.step({0: 0, 1: 0}))

    input('Windows: Ctrl_Z+Return')

    # Each policy can have a different configuration (including custom model)
    def gen_policy(i):
        config = {
            # "model": {
            #     "custom_model": ["model1", "model2"][i % 2],
            # },
            "gamma": random.choice([0.95, 0.99]),
        }
        return (None, obs_space, act_space, config)

    # Setup PPO with an ensemble of `num_policies` different policies
    policies = {
        "policy_{}".format(i): gen_policy(i)
        for i in range(args.num_policies)
    }
    policy_ids = list(policies.keys())

    tune.run(
        "PPO",
        stop={"training_iteration": args.num_iters},
        config={
            "env": "multi_cartpole",
            # "log_level": "DEBUG",
            "simple_optimizer": args.simple,
            "num_sgd_iter": 10,
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id: random.choice(policy_ids)),
            },
        },
    )
