import aws_cdk as core
import aws_cdk.assertions as assertions

from storyboard.storyboard_stack import StoryboardStack

# example tests. To run these tests, uncomment this file along with the example
# resource in storyboard/storyboard_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = StoryboardStack(app, "storyboard")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
