# RecyScore: An IoT-based Recycling Reward System
[![RecyScore](https://raw.githubusercontent.com/vaclisinc/RecyScore/94c3842ee217831b425d6b2e223086942097fd4a/RecyScore_preview.png)](https://youtu.be/Dq3dorVjYOg?t=178)
*Click on the picture to view our demo video*

---

## **Project Overview**
- RecyScore is an innovative IoT-based recycling reward system that uses Large Language Model (LLM) to identify and classify recyclable items.
- The system provides real-time feedback and rewards users for proper recycling practices, encouraging sustainable waste management.
- Feel free to scroll down the README or read the [slides](https://github.com/vaclisinc/RecyScore/blob/main/slides/RecyScore_slides.pdf) or [12-minute-presentation](https://youtu.be/Dq3dorVjYOg).
- Feel free to open our [website](http://your-recycling-stats-webapp.s3-website-us-east-1.amazonaws.com/) or with the demo account: `vaclis`, password: `vaclis`

## **Key Features**
![RecyScore_why_us](https://raw.githubusercontent.com/vaclisinc/RecyScore/b82890ac0d6df47886a749a73eb47afdfbc92adc/slides/RecyScore_why_us.jpg)
- Real-time object capturing and uploading using Raspberry Pi camera and official tablet
- AWS IoT Core integration for device status management on web
- AI-powered image analysis using OpenAI's LLM model
- Web-based dashboard for tracking recycling statistics
- Reward system for encouraging proper recycling practices

## **System Architecture**
![RecyScore_system_design](https://raw.githubusercontent.com/vaclisinc/RecyScore/5df611c89dd9c02b192cded52a30ddf01e5f709e/slides/RecyScore_System_Design.jpg)

## **Team Members**
- **Song-Ze, Yu** [(@vaclisinc)](http://github.com/vaclisinc): Raspberry Pi camera capturing and GUI, AWS ioT core and device shadow, website function writing, slide making and video editing.
- **Koying** [(@koyingtw)](https://github.com/koyingtw): LLM Lambda function, AWS DynamoDB, AWS API Gateway, S3 static web hosting.
- **Daniel Lin** [(@trkk28097402)](https://github.com/trkk28097402): ioT core SDK installing, slide making.

## **Getting Started**
1. Clone the repository
2. Set up your AWS credentials and environment variables (see `example_env.txt`)
3. Install required dependencies
4. Run the GUI on Raspberry Pi using `run.sh` (You may need to modfiy the python env directory.)

## **Project Structure**
```
RecyScore/
├── pi/               # Raspberry Pi related code
├── lambda/           # AWS Lambda functions
├── web/              # Web interface files
├── policy/           # AWS IAM policies
└── run.sh            # Startup script
```

## **Technologies Used**
- Python
- AWS IoT Core
- AWS Lambda
- AWS DynamoDB
- AWS API Gateway
- OpenAI API
- Raspberry Pi
- HTML/CSS/JavaScript
