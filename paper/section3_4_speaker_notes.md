# Speaker Script for Sections 3 and 4

[Slide 4: Methodology - Environment and Model]
"Now let's look at how we implemented this idea in Super Mario Bros.

Our environment is SuperMarioBros level 1, using the SIMPLE_MOVEMENT action set with seven discrete actions. Since the input is raw game images, we use an Atari-style preprocessing pipeline: convert frames to grayscale, resize them to 84 by 84, stack four consecutive frames, and normalize the pixel values.

We also make the reward sparse. the agent only receives a terminal reward based on its normalized forward distance. This makes exploration much harder and gives us a clearer test of whether SASR helps.

For the model, we first tried SASR with SAC-Discrete, but it was unstable. The policy often collapsed to one repeated action and stopped exploring. We therefore switched to PPO, whose on-policy updates worked better in this visual setting.

We also made several implementation changes. SASR performs KDE in the CNN feature space instead of raw pixels. We apply L2 normalization to keep feature scale stable, and use adaptive success classification plus warm-up gating, so shaping is not used too early.

One issue is distributional lag. The CNN encoder changes during training, so old stored features may not match the current feature space. To reduce this gap, we keep a small feature window and use FIFO success and failure buffers. This removes old features before they become too different from the current encoder."

[Slide 5: Experimental Results]
"Now we move to the results.

The plot compares Dueling DQN, PPO, and SASR plus PPO on the same sparse Mario task. DQN learns the slowest and plateaus around 0.6 episodic return. PPO reaches around 0.8, but still fails to complete the level within one million steps.

SASR plus PPO performs best. It reaches a return close to 1.0 at around 800 thousand steps, and is the only method that completes the level.

The main takeaway is that the memory of successful states gives the agent a denser exploration signal. Instead of relying only on the final sparse reward, the agent is guided toward states that resemble previous success.