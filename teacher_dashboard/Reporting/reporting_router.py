from fastapi.routing import APIRouter
from teacher_dashboard.Reporting.reporting_request_schema import ReportingResponse, LogReport
from fastapi.param_functions import Depends
from fastapi import Request
from teacher_dashboard.Reporting.reporting_service import reporting_service
from sqlalchemy.orm.session import Session
from teacher_dashboard.db_session import db_session, get_db
from teacher_dashboard.Assignment.dependencies.token_dependency import token_dependency
from teacher_dashboard.Reporting.reporting_request_schema import AssignmentClassOverviewRequest, \
    InsightsDownloadRequest, InsightsRequest, AssignmentStudentsRequest, AssignmentQuestionsRequest
from teacher_dashboard.db_session import request_auth_token

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/reporting/assignment",
    tags=["Reporting"]
)


@router.post("/logger", response_model=ReportingResponse)
async def report_logger(request: Request, report: LogReport, db: Session = Depends(get_db)):
    print(await request.json())
    print(report)
    logger.info('report_logs from solver = %r', report)
    db_session.set(db)
    return reporting_service.log_reports(report)


@router.get("/knowledge_gaps/{assignment_id}", dependencies=[Depends(token_dependency.validate_token),
                                                             Depends(token_dependency.role_teacher)])
async def knowledge_gaps_by_assignment(assignment_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    logger.info('assignment_id = %r', assignment_id)
    return reporting_service.get_assignment_kg(assignment_id)


@router.get("/problem_highlights/{assignment_id}", dependencies=[Depends(token_dependency.validate_token),
                                                                 Depends(token_dependency.role_teacher)])
async def problem_highlights(assignment_id: int, db: Session = Depends(get_db)):
    db_session.set(db)
    logger.info('assignment_id = %r', assignment_id)
    return reporting_service.get_problem_highlights(assignment_id)


@router.get("/terms/{term_code}", dependencies=[Depends(token_dependency.validate_token)])
async def get_ee_terms_details(term_code: str, db: Session = Depends(get_db)):
    db_session.set(db)
    logger.info('term_code = %r', term_code)
    return reporting_service.get_term_code_details(term_code)


@router.get("/insights", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_insights(insightsRequest: InsightsRequest = Depends(), user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(insightsRequest.auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(insightsRequest.dict()))

    response = reporting_service.get_insights(insightsRequest)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/insights/download", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_insights(insightsDownloadRequest: InsightsDownloadRequest = Depends(), user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(insightsDownloadRequest.auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(insightsDownloadRequest.dict()))

    response = reporting_service.download_insights(insightsDownloadRequest)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/overview", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_assignment_class_overview(assignmentClassOverviewRequest: AssignmentClassOverviewRequest = Depends(), user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(assignmentClassOverviewRequest.auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(
        assignmentClassOverviewRequest.dict()))

    response = reporting_service.get_assignment_class_overview(
        assignmentClassOverviewRequest)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/students", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_assignment_students(assignmentStudentsRequest: AssignmentStudentsRequest = Depends(), user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(assignmentStudentsRequest.auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(assignmentStudentsRequest.dict()))

    response = reporting_service.get_assignment_students(
        assignmentStudentsRequest)

    logger.debug("response: {}".format(response.dict()))

    return response


@router.get("/questions", dependencies=[Depends(token_dependency.validate_token), Depends(token_dependency.role_teacher)])
async def get_assignment_questions(getAssignmentQuestionsRequest: AssignmentQuestionsRequest = Depends(), user_id: str = Depends(token_dependency.get_user_id), db: Session = Depends(get_db)):
    db_session.set(db)
    request_auth_token.set(getAssignmentQuestionsRequest.auth_token)

    logger.debug("user_id: {}".format(user_id))
    logger.debug("data recieved:  {}".format(
        getAssignmentQuestionsRequest.dict()))

    response = reporting_service.get_assignment_questions(
        getAssignmentQuestionsRequest)

    logger.debug("response: {}".format(response.dict()))

    return response

