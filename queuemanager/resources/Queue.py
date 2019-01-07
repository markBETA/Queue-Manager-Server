from flask_restplus import Resource, Namespace
from werkzeug.exceptions import BadRequest
from queuemanager.db_manager import DBManagerError, DBInternalError, DBManager, UniqueConstraintError
from queuemanager.models.Queue import QueueSchema

api = Namespace("queues", description="Jobs related operations")

db = DBManager(autocommit=False)

queue_schema = QueueSchema()
queues_schema = QueueSchema(many=True)


@api.route("")
class QueueList(Resource):
    """
    /queues
    """
    @api.doc(id="getQueues")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns all queues in the database
        """
        try:
            queues = db.get_queues()
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return queues_schema.dump(queues).data, 200


@api.route("/<int:queue_id>")
class Queue(Resource):
    """
    /queues/<queue_id>
    """
    @api.doc(id="getQueue")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self, queue_id):
        """
        Returns the queue with id==queue_id
        """
        try:
            queue = db.get_queue(queue_id)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return queue_schema.dump(queue).data, 200


@api.route("/active")
class ActiveQueue(Resource):
    """
    /queues/active
    """
    @api.doc(id="getActiveQueue")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns the active queue
        """
        try:
            queue = db.get_queue(True)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return queue_schema.dump(queue).data, 200


@api.route("/active/jobs")
class ActiveQueueJobs(Resource):
    def get(self):
        """
        Returns the active queue jobs
        """
        pass


@api.route("/waiting")
class WaitingQueue(Resource):
    """
    /queues/waiting
    """
    @api.doc(id="getWaitingQueue")
    @api.response(200, "Success")
    @api.response(500, "Unable to read the data from the database")
    def get(self):
        """
        Returns the waiting queue
        """
        try:
            queue = db.get_queue(False)
        except DBInternalError:
            return {'message': 'Unable to read the data from the database'}, 500

        return queue_schema.dump(queue).data, 200
