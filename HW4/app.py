from flask import Flask, Blueprint, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource, fields

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ERROR_404_HELP"] = False
app.config["RESTX_JSON"] = {"ensure_ascii": False}

db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    # HW4코드입니다.
    note = db.Column(db.String(500), default="")
    done = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Todo {self.id} {self.text}>"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        todo = Todo(text=request.form["todo"], note=request.form.get("note", ""))
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("index"))

    todos = Todo.query.all()
    return render_template("index.html", todos=todos)


@app.route("/delete/<int:id>")
def delete(id):
    todo = db.get_or_404(Todo, id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:id>")
def toggle(id):
    todo = db.get_or_404(Todo, id)
    todo.done = not todo.done
    db.session.commit()
    return redirect(url_for("index"))


# ----------------------------------------------------------------- API
# Blueprint로 한번 감싸고 거기에 Api를 붙입니다.
# 이렇게 해야 /api 아래에서만 JSON이 나오고, 위의 화면 라우트는 그대로 남습니다.
api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_bp,
    version="1.0",
    title="Todo API",
    description="4장에서만든todo 앱의API",
    doc="/docs",  # 문서는 /api/docs에 열립니다
)
ns = api.namespace("todos", description="할일하나하나를다루는곳")


# 주고받을 데이터의 모양입니다. 이것이 곧 문서가 됩니다.
todo_model = api.model(
    "Todo",
    {
        "id": fields.Integer(readonly=True, description="줄번호. 서버가붙입니다"),
        "text": fields.String(
            required=True, description="할일글자", example="우유사기"
        ),
        "done": fields.Boolean(description="완료여부", example=False),
        # HW4코드입니다.
        "note": fields.String(description="설명", example="2번째챕터끝"),
    },
)
todo_input = api.model(
    "TodoInput",
    {
        "text": fields.String(
            required=True, description="할일글자", example="우유사기"
        ),
        "done": fields.Boolean(description="완료여부", example=False),
        # HW4코드입니다.
        "note": fields.String(description="설명", example="2번째챕터끝"),
    },
)


@ns.route("/")
class TodoList(Resource):
    @ns.doc("목록보기")
    # HW4코드입니다.
    @ns.param("done", "true면완료한것만, false면안한것만")
    @ns.marshal_list_with(todo_model)
    def get(self):
        """done을주면걸러서돌려준다"""
        # HW4코드입니다.
        q = Todo.query
        done = request.args.get("done")
        if done is not None:
            q = q.filter_by(done=(done.lower() == "true"))
        return q.all()

    @ns.doc("새로만들기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        """할일을하나만든다"""
        todo = Todo(
            text=api.payload["text"],
            done=api.payload.get("done", False),
            # HW4코드입니다.
            note=api.payload.get("note", ""),
        )
        db.session.add(todo)
        db.session.commit()
        return todo, 201, {"Location": f"/api/todos/{todo.id}"}


@ns.route("/<int:id>")
@ns.param("id", "할일의줄번호")
@ns.response(404, "그번호의할일이없습니다")
class TodoItem(Resource):
    @ns.doc("하나보기")
    @ns.marshal_with(todo_model)
    def get(self, id):
        """할일하나를돌려준다"""
        return get_or_abort(id)

    @ns.doc("통째로바꾸기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model)
    def put(self, id):
        """할일하나를통째로바꾼다. 보내지않은칸은기본값이된다"""
        todo = get_or_abort(id)
        todo.text = api.payload["text"]
        todo.done = api.payload.get("done", False)
        db.session.commit()
        return todo

    @ns.doc("일부만바꾸기")
    @ns.expect(todo_input)
    @ns.marshal_with(todo_model)
    def patch(self, id):
        """보낸칸만바꾼다. 완료표시를뒤집을때씁니다"""
        todo = get_or_abort(id)
        if "text" in api.payload:
            todo.text = api.payload["text"]
        if "done" in api.payload:
            todo.done = api.payload["done"]
        # HW4코드입니다.
        if "note" in api.payload:
            todo.note = api.payload["note"]
        db.session.commit()
        return todo

    @ns.doc("지우기")
    @ns.response(204, "지웠습니다. 돌려줄내용이없습니다")
    def delete(self, id):
        """할일하나를지운다"""
        todo = get_or_abort(id)
        db.session.delete(todo)
        db.session.commit()
        return "", 204


def get_or_abort(id):
    """없는번호면404를JSON으로돌려준다."""
    todo = db.session.get(Todo, id)
    if todo is None:
        ns.abort(404, f"{id} 번할일이없습니다")
    return todo


app.register_blueprint(api_bp)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
