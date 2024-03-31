#!/usr/bin/env python3
import aws_cdk as cdk

from storyboard.storyboard_stack import StoryboardAPIStack

app = cdk.App()
StoryboardAPIStack(app, "StoryboardAPIStack")

app.synth()