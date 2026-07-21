
def build_header():
    with gr.Group():
            with gr.Row(equal_height=True):

                # Logo 
                with gr.Column(scale=0, min_width=100):
                    gr.Image(
                        "images/logo.png",
                        container=False,
                        width=65,
                        height=65,
                        interactive=False,
                        buttons=[],
                        show_label=False
                    )

                # Title
                with gr.Column(scale=4):
                    gr.Markdown(
                        """
                        <div style="padding-top: 3px;">
                            <h1 style="margin-bottom: 0;">
                                Grade Tracker
                            </h1>
                            <p style="margin-top: 0; color: gray;">
                                Academic Management Dashboard
                            </p>
                        </div>
                        """
                    )

                # Version Display
                with gr.Column(scale=1, min_width=150):
                    gr.Markdown(
                        """
                        <div style="text-align:right">
                        v0.785
                        </div>
                        """
                    )