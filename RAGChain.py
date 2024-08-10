
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from DocLoader import docload
from RAG_VectorDB import vectordb

class rag_chain():
    def __init__(self, llm, retriever, session_ids, store):
        self.llm = llm
        self.retriever = retriever
        self.session_ids = session_ids
        self.store = store
        self.prompt = PromptTemplate.from_template(
                                                    """
                                                        당신은 가계부 역할과 카드 추천을 동시에 하는 챗봇입니다.

                                                        - 질문에 특정 카테고리만 언급되었을 경우, 해당 카테고리에서 모든 날짜에 고객번호 1번이 쓴 금액 총합을 알려주세요.
                                                            - 예: "내가 카페에서 쓴 금액은 얼마인가요?"라고 물어보면, 고객번호 1번이 모든 날짜에 카페에서 쓴 총 금액을 답변하세요.
                                                        - 질문에 특정 날짜만 언급되었을 경우, 해당 날짜에 모든 카테고리에서 고객번호 1번이 쓴 금액 총합을 알려주세요.
                                                            - 예: "내가 2023년 5월 1일에 쓴 금액은 얼마인가요?"라고 물어보면, 고객번호 1번이 2023년 5월 1일에 모든 카테고리에서 쓴 총 금액을 답변하세요.
                                                        - 질문에 카테고리와 날짜가 동시에 언급되었을 경우, 해당 날짜에 해당 카테고리에서 고객번호 1번이 쓴 금액 총합을 알려주세요.
                                                            - 예: "내가 2023년 5월 1일에 카페에서 쓴 금액은 얼마인가요?"라고 물어보면, 고객번호 1번이 2023년 5월 1일에 카페에서 쓴 총 금액을 답변하세요.
                                                        - 사용자가 비교나 계산을 해달라고 요청하면 0원이더라도 무조건 비교나 계산을 해줘야 합니다.
                                                        - 카드 추천은 사용자가 카드 추천이나 혜택에 대해 물어봤을 때만 하세요. 단순 비교나 계산 질문일 경우 계산 결과만 답하고 카드추천을 하면 안됩니다.
                                                            - 예: "내가 카페에서 얼마 썼어", 대답: "고객님은 카페에 24,600원 썼습니다."
                                                            - 예: "나에게 맞는 카드가 뭐야?", 대답: "고객님께 맞는 카드는 체크카드, 청춘대로, BeVV 입니다."
                                                            - 예: "나에게 혜택이 좋은 카드가 뭐야?", 대답: "고객님께 맞는 카드는 우리동네, BeVV, 트래블러스 입니다."
                                                        - 모든 대답은 높임말을 사용해야 합니다.

                                                        - 답은 무조건 한글로 해야 합니다. 중요사항입니다. 한글로만 답해야 합니다

                                                        다음의 retrieved context를 이용하여 질문에 답하세요.
                                                        - 무조건 한글로만 답해야 합니다

                                                        #Previous Chat History : {chat_history}
                                                        #Question : {question}
                                                        #Context : {context}
                                                        #Answer :
                                                    
                                                    """
                                                    )
        self.chain = ({"context" : itemgetter("question") | self.retriever, 
                       "question" : itemgetter("question"), 
                       "chat_history" : itemgetter("chat_history"),} 
                       | self.prompt 
                       | self.llm 
                       | StrOutputParser())
    
    def get_session_history(self):
        print(f"[대화 세션 ID] : {self.session_ids}")
        if self.session_ids not in self.store:
            self.store[self.session_ids] = ChatMessageHistory()
        return self.store[self.session_ids]
    
    def get_rag_history(self):
        rag_with_history = RunnableWithMessageHistory(
            self.chain,
            self.get_session_history,
            input_messages_key = "question",
            history_messages_key = "chat_history",
        )
        return rag_with_history